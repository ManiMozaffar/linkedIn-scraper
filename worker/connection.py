import random
import json

import requests
from playwright.async_api import async_playwright
import loguru
import pytz


import prompt
import helpers
import xpaths
import constants


async def create_ads(
        ads_id, location, body, company_name, title, source, employement_type,
        level, country
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
    """
    async with async_playwright() as main_driver:
        chatgpt_browser = await main_driver.firefox.launch(
            headless=True,
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
        loguru.logger.info(f"Fetched Data {ads_id}")
        loguru.logger.info(f"Started ChatGPT {ads_id}")
        await chatgpt_page.goto("https://chatbot.theb.ai/#/chat/")
        await helpers.safe_fill_form(
            chatgpt_page, xpaths.GPT_FILL,
            f"""
            Company Name is {company_name}

            {prompt.CHATGPT}
            {body}
            """,
            timeout=5000
        )
        await chatgpt_page.locator(xpaths.GPT_BUTTON).click()
        response = None
        while response is None:
            event = await chatgpt_page.wait_for_event("response")
            if "chat-process" in event.url:
                response = event

        await response.finished()
        result = await response.text()
        lines = list(filter(None, result.split('\n')))
        last_json_obj = json.loads(lines[-1])
        data = {
            "ads_id": ads_id,
            "location": location,
            "country": country,
            "body": last_json_obj["text"],
            "company_name": company_name,
            "title": title,
            "source": source,
            "employement_type": employement_type,
            "level": level
        }
        resp = requests.post(f"{constants.HOST}/api/ads", json=data)
        if resp.status_code != 200:
            loguru.logger.error(resp.text)
