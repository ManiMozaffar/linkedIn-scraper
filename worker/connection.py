import requests
from playwright.async_api import async_playwright
import constants
import random
import pytz
import helpers
import xpaths
import json
import loguru

host = "http://127.0.0.1:8000"


async def create_ads(
        ads_id, location, body, company_name, title, source, employement_type,
        level, country, proxy=None
):
    async with async_playwright() as main_driver:
        chatgpt_browser = await main_driver.firefox.launch(
            headless=False,
            args=['--start-maximized'],
            firefox_user_prefs=constants.FIREFOX_SETTINGS
        )
        timezone_id = random.choice(pytz.all_timezones)
        chatgpt_context = await chatgpt_browser.new_context(
            timezone_id=timezone_id,
            accept_downloads=True,
            is_mobile=False,
            has_touch=False,
            proxy=proxy
        )
        chatgpt_page = await chatgpt_context.new_page()
        await chatgpt_page.add_init_script(
            constants.SPOOF_FINGERPRINT % helpers.generate_device_specs()
        )
        loguru.logger.info(f"Fetched Data {ads_id}")
        loguru.logger.info(f"Started ChatGPT {ads_id}")
        await chatgpt_page.goto("https://chatbot.theb.ai/#/chat/")
        await helpers.safe_fill_form(
            chatgpt_page, xpaths.GPT_FILL,
            f"""
            PROMPTS:
            1. Act as recruiter who rewievs other advertisement
            2. List Hard Skill required for this job advertisement
            3. DO NOT write anything else in response than the list

            Job Description:
            {body}
            """
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
        last_json_str = lines[-1]
        last_json_obj = json.loads(last_json_str)
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
        resp = requests.post(f"{host}/api/ads", json=data)
        if resp.status_code != 200:
            print(resp.text)
