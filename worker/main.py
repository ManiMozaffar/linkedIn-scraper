import asyncio
from playwright.async_api import async_playwright
import random
import pytz
import helpers
import xpaths
import connection
import constants
import loguru


@helpers.recursive_handler
async def scrape_linkedin(*args, **kwargs):
    used_countries = []
    while True:
        async with async_playwright() as driver:
            country, used_countries = helpers.get_country(used_countries)
            print(country)
            browser = await driver.firefox.launch(
                headless=True,
                args=[
                    '--start-maximized',
                    '--foreground',
                    '--disable-backgrounding-occluded-windows'
                ],
                firefox_user_prefs=constants.FIREFOX_SETTINGS
            )

            timezone_id = random.choice(pytz.all_timezones)
            context = await browser.new_context(
                timezone_id=timezone_id,
                accept_downloads=True,
                is_mobile=False,
                has_touch=False,
                proxy=connection.get_random_proxy()
            )

            page = await context.new_page()
            await page.bring_to_front()
            # screen_width, screen_height = pyautogui.size()
            await page.set_viewport_size(
                {
                    "width": 1920,
                    "height": 1080
                }
            )

            await page.add_init_script(
                constants.SPOOF_FINGERPRINT % helpers.generate_device_specs()
            )
            await page.goto(helpers.get_url(location=country))
            total_num = int(
                await page.locator(xpaths.JOB_TOTAL_NUM).text_content(
                    timeout=5000
                )
            )
            total_num = 100 if total_num > 100 else total_num

            loguru.logger.info(f"Found {total_num} related jobs")
            for index in range(1, total_num+1):
                await page.locator(f'({xpaths.JOB_LI})[{index}]').hover(
                    timeout=5000
                )
                await page.locator(f'({xpaths.JOB_LI})[{index}]').click(
                    timeout=5000
                )
                ads_id = await page.locator(
                    f'({xpaths.JOB_LI})[{index}]//div[@data-entity-urn]'
                ).get_attribute('data-entity-urn')
                ads_id = ads_id.split("urn:li:jobPosting:")[1]
                if not connection.does_ads_exists(ads_id):
                    company_name = await helpers.safe_get_element_text(
                        page, xpaths.COMPANY_NAME, timeout=5000
                    )
                    location = await helpers.safe_get_element_text(
                        page, xpaths.LOCATION, timeout=5000
                    )
                    title = await helpers.safe_get_element_text(
                        page, xpaths.TITLE, timeout=5000
                    )
                    # level = await helpers.safe_get_element_text(
                    #     page, xpaths.SENIORITY_LEVEL, timeout=100
                    # )
                    # employement_type = await helpers.safe_get_element_text(
                    #     page, xpaths.EMPLOYEMENT_TYPE, timeout=100
                    # )
                    await page.locator(xpaths.SHOW_MORE).click(timeout=5000)
                    info = await helpers.get_element_text(
                        page, xpaths.BODY_INFO, False, timeout=5000
                    )
                    await connection.create_ads(
                        ads_id, location, info.strip(), company_name,
                        title, 1, employement_type="", level="",
                        country=country,
                    )
                    loguru.logger.info(f"Finished {ads_id}")
                    await asyncio.sleep(random.randint(4, 10))

                else:
                    loguru.logger.info(f"{ads_id} Already exists")

asyncio.run(scrape_linkedin())
