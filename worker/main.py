import asyncio
from playwright.async_api import async_playwright
import random
import pytz
import helpers
import xpaths
import connection


async def scrape_linkedin(proxy=None, *args, **kwargs):
    while True:
        async with async_playwright() as p:
            country = helpers.get_country()
            print(country)
            browser = await p.firefox.launch(
                headless=True,
                args=['--start-maximized'],
                firefox_user_prefs={
                    "pdfjs.disabled": False,
                    "browser.taskbar.lists.enabled": True,
                    "browser.taskbar.lists.frequent.enabled": True,
                    "browser.taskbar.lists.recent.enabled": True,
                    "browser.taskbar.lists.tasks.enabled": True,
                    "browser.taskbar.lists.maxListItemCount": 10,
                },
            )

            timezone_id = random.choice(pytz.all_timezones)
            context = await browser.new_context(
                timezone_id=timezone_id,
                accept_downloads=True,
                is_mobile=False,
                has_touch=False,
                proxy=proxy
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
            hardware_spoof_script = '''
                (() => {
                    delete navigator.__proto__.webdriver;
                    Object.defineProperty(navigator, 'deviceMemory', { value: %d, configurable: true });

                    const originalHardwareConcurrency = navigator.hardwareConcurrency;
                    const originalPropertyDescriptor = Object.getOwnPropertyDescriptor(
                        Navigator.prototype, 'hardwareConcurrency'
                    );
                    Object.defineProperty(Navigator.prototype, 'hardwareConcurrency', {
                        get: function() {
                            return %d;
                        },
                        enumerable: originalPropertyDescriptor.enumerable,
                        configurable: originalPropertyDescriptor.configurable,
                    });

                    const originalWorker = window.Worker;
                    window.Worker = new Proxy(originalWorker, {
                        construct(target, args) {
                            const worker = new target(...args);
                            const handleMessage = (event) => {
                                if (event.data === 'spoofHardwareConcurrency') {
                                    worker.postMessage(navigator.hardwareConcurrency);
                                }
                            };
                            worker.addEventListener('message', handleMessage);
                            return worker;
                        }
                    });
                })();
            ''' % helpers.generate_device_specs()
            await page.add_init_script(hardware_spoof_script)
            await page.goto(helpers.get_url(location=country))
            total_num = int(await page.locator(xpaths.JOB_TOTAL_NUM).text_content())
            total_num = 100 if total_num > 100 else total_num
            for index in range(1, total_num+1):
                    await page.locator(f'({xpaths.JOB_LI})[{index}]').click()
                    ads_id = await page.locator(
                        f'({xpaths.JOB_LI})[{index}]//div[@data-entity-urn]'
                    ).get_attribute('data-entity-urn')
                    ads_id = ads_id.split("urn:li:jobPosting:")[1]
                    level = await helpers.safe_get_element_text(
                        page, xpaths.SENIORITY_LEVEL
                    )
                    employement_type = await helpers.safe_get_element_text(
                        page, xpaths.EMPLOYEMENT_TYPE,
                    )
                    company_name = await helpers.safe_get_element_text(
                        page, xpaths.COMPANY_NAME
                    )
                    location = await helpers.safe_get_element_text(
                        page, xpaths.LOCATION
                    )
                    title = await helpers.safe_get_element_text(
                        page, xpaths.TITLE
                    )
                    await asyncio.sleep(random.randint(1, 2))
                    await page.locator(xpaths.SHOW_MORE).click()
                    info = await helpers.get_element_text(
                        page, xpaths.BODY_INFO, False
                    )
                    connection.create_ads(
                        ads_id, location, info.strip(), company_name,
                        title, 1, employement_type, level, country
                    )
                    print(f"Finished {ads_id}")
                    await asyncio.sleep(random.randint(3, 12))

asyncio.run(scrape_linkedin())
