import asyncio
import random


from playwright.async_api import async_playwright
import pytz
import loguru


import helpers
import xpaths
import connection
import constants


async def scrape_linkedin(used_countries: list = [], *args, **kwargs) -> list:
    """
    Scrape LinkedIn job postings for different countries.

    :param used_countries: List of countries that have been used in previous
           scraping.

    :return: List of used countries after scraping.
    """
    try:
        async with async_playwright() as driver:
            country, used_countries = helpers.get_country(used_countries)
            loguru.logger.info(country)
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
                proxy=helpers.get_random_proxy()
            )

            page = await context.new_page()
            await page.bring_to_front()
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
            all_ads = await page.locator(xpaths.JOB_LI).all()
            loguru.logger.info(f"Found {len(all_ads)} Advertisements")
            exists = 0
            for index, div in enumerate(all_ads):
                await asyncio.sleep(2)
                if index == 100 or exists == 7:
                    break
                await div.click(
                    timeout=5000
                )
                title_a_tag = page.locator(xpaths.JOB_ID_A_TAG)
                ads_id = await title_a_tag.get_attribute('href')
                ads_id = ads_id.split("?refId")[0].split("-")[-1]
                if not helpers.does_ads_exists(ads_id):
                    company_name = await helpers.safe_get_element_text(
                        page, xpaths.COMPANY_NAME, timeout=5000
                    )
                    location = await helpers.safe_get_element_text(
                        page, xpaths.LOCATION, timeout=5000
                    )
                    title = await helpers.safe_get_element_text(
                        page, xpaths.TITLE, timeout=5000
                    )
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

                else:
                    loguru.logger.info(f"{ads_id} Already exists")
                    exists += 1

        return used_countries
    except Exception:
        return await scrape_linkedin(used_countries)


async def run_scrapers(workers: int = 1):
    tasks = []
    for i in range(workers):
        tasks.append(asyncio.create_task(scrape_linkedin()))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    while True:
        used_countries = asyncio.run(scrape_linkedin(workers=1))
