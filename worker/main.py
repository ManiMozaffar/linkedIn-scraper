import asyncio
from playwright.async_api import async_playwright
import random
import pytz
import utils
import xpaths


def generate_device_specs():
    random_ram = random.choice([1, 2, 4, 8, 16, 32, 64])
    max_hw_concurrency = random_ram * 2 if random_ram < 64 else 64
    random_hw_concurrency = random.choice([1, 2, 4, max_hw_concurrency])
    return (random_ram, random_hw_concurrency)


async def get_element_text(page, xpath, replace=True):
    result: str = await page.locator(xpath).text_content()
    if replace:
        return result.strip().replace("\n", "")
    else:
        return result


async def get_firefox(proxy=None, *args, **kwargs):
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=False,
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
        ''' % generate_device_specs()
        await page.add_init_script(hardware_spoof_script)
        await page.goto(utils.get_url())
        total_num = int(await page.locator(xpaths.JOB_TOTAL_NUM).text_content())
        total_num = 100 if total_num > 100 else total_num
        for index in range(1, total_num+1):
            await page.locator(f'({xpaths.JOB_LI})[{index}]').click()
            level = await get_element_text(page, xpaths.SENIORITY_LEVEL)
            type = await get_element_text(page, xpaths.EMPLOYEMENT_TYPE)
            await asyncio.sleep(random.randint(1, 2))
            await page.locator(xpaths.SHOW_MORE).click()
            info = await get_element_text(page, xpaths.BODY_INFO, False)
            company_name = await get_element_text(page, xpaths.COMPANY_NAME)
            location = await get_element_text(page, xpaths.LOCATION)
            print(location, company_name, level, type)
            print(info)
            print("--------------------------------")
            await asyncio.sleep(random.randint(3, 12))


asyncio.run(get_firefox())
