import requests
from playwright.async_api import async_playwright
from playwright._impl._api_structures import ProxySettings
import constants
import random
import pytz
import helpers
import xpaths
import json
import loguru

host = "http://127.0.0.1:8000"


def does_ads_exists(ads):
    return requests.get(f"{host}/api/ads/{ads}").status_code == 200


async def create_ads(
        ads_id, location, body, company_name, title, source, employement_type,
        level, country, proxy=None
):
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
            proxy=proxy
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
            PROMPTS:
            1. Act as recruiter who rewievs other advertisement
            2. List Hard Skill required for this job advertisement, write them briefly in fewer words
            3. DO NOT write anything else in response than the list
            4. Translate To English If Needed
            5. At first word, write 'Sponser Status: Yes' if you think the company offers visa sponsership, 
            and ''Sponser Status: N/A' if you're not sure, and 'Sponser Status: No' if you're sure it doesn't. 
            6. Make sure you write the sponser status at least one of these. 

            
            SAMPLE OUTOUT:
            Sponser Status: Yes
            1. Python
            2. Django


            Job Description:
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
        resp = requests.post(f"{host}/api/ads", json=data)
        if resp.status_code != 200:
            print(resp.text)


def create_proxy_url(proxy_dict):
    return ProxySettings(
        server=f"http://{proxy_dict['ip_address']}:{proxy_dict['port']}",
        username=proxy_dict['username'], password=proxy_dict['password']
    )


def get_random_proxy():
    proxy_dict = requests.get(
        f"{host}/api/proxy?order_by=?&page=1&per_page=1"
    ).json()["results"][0]
    return create_proxy_url(proxy_dict)
