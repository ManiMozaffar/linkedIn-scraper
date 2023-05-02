import random
import json
import asyncio
import re

import requests
from playwright.async_api import async_playwright, Page, Response
import loguru
import pytz


import prompt
import helpers
import xpaths
import constants
import exceptions
import decorators
import enums


@decorators.async_timeout(120)
async def get_response_from_theb_ai(chatgpt_page: Page) -> dict:
    response = None
    while response is None:
        event = await chatgpt_page.wait_for_event("response")
        if "chat-process" in event.url:
            response: Response = event

    await response.finished()
    result = await response.text()
    assert response.status == 200
    lines = list(filter(None, result.split('\n')))
    return json.loads(lines[-1])


async def create_ads(
        ads_id, location, body, company_name, title, source, employement_type,
        level, country, job_mode: enums.JobModels, worker_id: int = 1,
        headless: bool = True
) -> None:
    """
    Create a new advertisement with the given parameters and save it to the db.

    :param ads_id: The advertisement ID.
    :param location: The location of the job.
    :param body: The body text of the advertisement.
    :param company_name: The name of the company posting the job.
    :param title: The job title.
    :param source: The source of the advertisement.
    :param employement_type: The type of employment
    :param level: The seniority level of the job.
    :param country: The country where the job is located.
    :param job_mode: The job's mode (remote, etc)
    """
    async with async_playwright() as main_driver:
        chatgpt_browser = await main_driver.firefox.launch(
            headless=headless,
            args=[
                '--start-maximized',
                '--foreground',
                '--disable-backgrounding-occluded-windows'
            ],
            firefox_user_prefs=constants.FIREFOX_SETTINGS
        )
        timezone_id = random.choice(pytz.all_timezones)
        chatgpt_context = await chatgpt_browser.new_context(
            timezone_id=timezone_id,
            accept_downloads=True,
            is_mobile=False,
            has_touch=False,
            proxy=helpers.get_random_proxy()
        )
        chatgpt_page = await chatgpt_context.new_page()
        await chatgpt_page.add_init_script(
            constants.SPOOF_FINGERPRINT % helpers.generate_device_specs()
        )
        await chatgpt_page.bring_to_front()
        loguru.logger.info(f"[WORKER {worker_id}] Fetched Data {ads_id}")
        loguru.logger.info(f"[WORKER {worker_id}] Started ChatGPT {ads_id}")
        await chatgpt_page.goto("https://chatbot.theb.ai/#/chat/")
        await asyncio.sleep(1)
        await helpers.safe_fill_form(
            chatgpt_page, xpaths.GPT_FILL,
            f"""
{prompt.analyze_ads(company_name, body)} \n
            """,
            timeout=5000
        )
        await chatgpt_page.locator(xpaths.GPT_BUTTON).click()
        first_resp = await get_response_from_theb_ai(chatgpt_page)
        await chatgpt_page.locator(xpaths.GPT_NEW_CHAT).click()
        await asyncio.sleep(1)
        await helpers.safe_fill_form(
            chatgpt_page, xpaths.GPT_FILL,
            f"""
{prompt.get_tag_ads(title, first_resp["text"], helpers.get_all_keywords())}
            """,
            timeout=5000
        )
        await chatgpt_page.locator(xpaths.GPT_BUTTON).click()
        second_resp = await get_response_from_theb_ai(chatgpt_page)
        try:
            second_resp_list = None
            second_resp_text = re.search(
                r'\{.*\}', second_resp["text"].replace("'", "\"")
            )
            if not second_resp_text:
                raise exceptions.NoJsonFound(
                    "No valid JSON object found in the last line"
                )
            second_resp_text = second_resp_text.group()
            second_resp_list: list = json.loads(second_resp_text)["keywords"]
            if "#Yes" in first_resp["text"]:
                second_resp_list.append("yes")
            elif "#No" in first_resp["text"]:
                second_resp_list.append("no")
            elif "#NA" in first_resp["text"]:
                second_resp_list.append("na")
            second_resp_list.append(job_mode.lower_case_name)

            second_resp_list.append(helpers.format_country(
                country
            ))
            hashtags = ' '.join(set(f"#{tag}" for tag in second_resp_list))
            body = f"""
{first_resp["text"]}


{hashtags}
"""
            print(hashtags)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            body = first_resp["text"]
            loguru.logger.error(
                f"[WORKER {worker_id}] {e.__name__} raised on second resp"
            )
            loguru.logger.error(
                f"\n\n [WORKER {worker_id}] second_resp={second_resp}\n"
            )

        data = {
            "ads_id": ads_id,
            "location": location,
            "country": country,
            "body": body,
            "company_name": company_name,
            "title": title,
            "source": source,
            "employement_type": employement_type,
            "level": level,
        }
        if second_resp_list:
            data["keywords"] = second_resp_list
        resp = requests.post(f"{constants.HOST}/api/ads", json=data)
        if resp.status_code != 200:
            loguru.logger.error(
                f"WORKER {worker_id}] Status not 200: {resp.text}"
            )

        await asyncio.sleep(1)
