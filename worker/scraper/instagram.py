
from playwright.async_api import async_playwright
import helpers
import loguru
import constants
import random
import pytz
import asyncio


async def scrape_linkedin(
        worker_id: int, info=None,
        only_popular=False, headless=False, *args, **kwargs
):
    """
    Scrape LinkedIn job postings for different countries.

    :param worker_id: ID of the worker executing the scraping.
    :param info: Cached info, if you wish to repeat the process.
    :param only_popular: Only use popular countries.
    """
    try:
        async with async_playwright() as driver:
            if info is None:
                info = helpers.get_country_and_job(only_popular)

            loguru.logger.info(
                f"[WORKER {worker_id}] This round is: {info}"
            )
            country, job, job_mode = info
            browser = await driver.chromium.launch(
                headless=headless,
                args=[
                    '--start-maximized',
                    '--foreground',
                    '--disable-backgrounding-occluded-windows'
                ],
                # firefox_user_prefs=constants.FIREFOX_SETTINGS
            )

            timezone_id = random.choice(pytz.all_timezones)
            context = await browser.new_context(
                timezone_id=timezone_id,
                accept_downloads=True,
                is_mobile=False,
                has_touch=False,
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
            await page.goto("https://www.instagram.com/mozaffar__m42")
            input("")

            # if await helpers.does_element_exists(page, xpaths.NEED_LOGIN):
            #     loguru.logger.info(f"[WORKER {worker_id}] Login Required!")
            #     return await scrape_linkedin(
            #         worker_id=worker_id, only_popular=only_popular,
            #         headless=headless, info=info
            #     )

            # all_ads = await page.locator(xpaths.JOB_LI).all()
            # loguru.logger.info(
            #     f"[WORKER {worker_id}] Found {len(all_ads)} Advertisements"
            # )
            # exists = 0
            # for index, div in enumerate(all_ads):
            #     await asyncio.sleep(2)
            #     if index == 100 or exists == 7:
            #         break
            #     await div.click(
            #         timeout=5000
            #     )
            #     title_a_tag = page.locator(xpaths.JOB_ID_A_TAG)
            #     ads_id = await title_a_tag.get_attribute('href')
            #     ads_id = ads_id.split("?refId")[0].split("-")[-1]
            #     if not helpers.does_ads_exists(ads_id):
            #         company_name = await helpers.safe_get_element_text(
            #             page, xpaths.COMPANY_NAME, timeout=5000
            #         )
            #         location = await helpers.safe_get_element_text(
            #             page, xpaths.LOCATION, timeout=5000
            #         )
            #         title = await helpers.safe_get_element_text(
            #             page, xpaths.TITLE, timeout=5000
            #         )
            #         await page.locator(xpaths.SHOW_MORE).click(timeout=5000)
            #         info = await helpers.get_element_text(
            #             page, xpaths.BODY_INFO, False, timeout=5000
            #         )
            #         await connection.create_ads(
            #             ads_id, location, info.strip(), company_name,
            #             title, 1, employement_type="", level="",
            #             country=country, job_mode=job_mode
            #         )
            #         loguru.logger.info(
            #             f"[WORKER {worker_id}] Finished {ads_id}"
            #         )

            #     else:
            #         loguru.logger.info(
            #             f"[WORKER {worker_id}] {ads_id} Already exists"
            #         )
            #         exists += 1

        return
    except helpers.PlayWrightTimeOutError:
        pass
    except Exception as e:
        loguru.logger.error(e)
    finally:
        return await scrape_linkedin(
            worker_id=worker_id, only_popular=only_popular,
            headless=headless
        )


async def run_scrapers():
    await scrape_linkedin(worker_id=1, only_popular=False, headless=False)


if __name__ == "__main__":
    args = helpers.parse_arguments()
    used_countries = asyncio.run(run_scrapers())
