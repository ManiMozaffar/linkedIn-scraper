import json
from typing import Union, List
import logging
import asyncio

from playwright.async_api import Page, Response, TimeoutError
import httpx


from crawlers.linkedin import xpaths, prompt
from crawlers.linkedin.models import LinkedinData, LinkedinURLData
from crawlers.linkedin.utils import (
    get_all_keywords,
    process_thebai_responses_to_text
)
from core.browser import PlayWrightCrawler
from core.decorators import add_task, async_timeout


class AdsDataGateway(PlayWrightCrawler):
    inputs: LinkedinURLData

    @property
    def data(self) -> Union[LinkedinData, None]:
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @add_task(level=0)
    async def get_adds_info(
        self,
        page: Page,
        **_
    ) -> None:
        await page.goto(self.inputs.url)
        await self.click_xpath(page, xpaths.SHOW_MORE)
        tasks = [
            self.read_from_xpath(page, xpaths.LOCATION, raise_error=True),
            self.read_from_xpath(page, xpaths.BODY_INFO, raise_error=True),
            self.read_from_xpath(page, xpaths.COMPANY_NAME, raise_error=True),
            self.read_from_xpath(page, xpaths.TITLE, raise_error=True),
            self.read_from_xpath(page, xpaths.SENIORITY_LEVEL)
        ]
        results = await asyncio.gather(*tasks)
        self.data = LinkedinData(
            ads_id=self.inputs.ads_id,
            location=results[0],
            country=self.inputs.country,
            body=results[1],
            company_name=results[2],
            title=results[3],
            employement_type=self.inputs.job_mode,
            level=results[4].strip(),
        )

    @add_task(level=1)
    async def process_adds_info(
        self,
        page: Page,
        **_
    ) -> None:
        """
        This task will process the information gathered in below level,
        then process them using thebai
        """
        if isinstance(self.data, LinkedinData):
            await page.goto("https://chatbot.theb.ai/#/chat/")
            await self.fill_form(
                page=page,
                xpath=xpaths.GPT_FILL,
                text=prompt.analyze_ads(
                    self.data.company_name, self.data.body
                ),
                raise_error=True
            )
            await self.click_xpath(page, xpaths.GPT_BUTTON, raise_error=True)
            first_resp = await self.get_response_from_theb_ai(page)
            await self.click_xpath(page, xpaths.GPT_NEW_CHAT, raise_error=True)
            await asyncio.sleep(0.2)
            await self.fill_form(
                page=page,
                xpath=xpaths.GPT_FILL,
                text=f"""{prompt.get_tag_ads(
                    self.data.title, first_resp["text"], get_all_keywords()
                )}"""
            )
            await asyncio.sleep(0.2)
            await self.click_xpath(page, xpaths.GPT_BUTTON, raise_error=True)
            second_resp = await self.get_response_from_theb_ai(page)
            text, hashtags = process_thebai_responses_to_text(
                first_resp, second_resp, self.data.country,
                self.data.employement_type.value
            )
            if text:
                self.data.body = text
            if hashtags:
                self.data.keywords = hashtags

    @async_timeout(120)
    async def get_response_from_theb_ai(self, chatgpt_page: Page) -> dict:
        try:
            response = None
            while response is None:
                event = await chatgpt_page.wait_for_event("response")
                if "chat-process" in event.url:
                    response: Response = event
            result = await response.text()
            lines = list(filter(None, result.split('\n')))
            return json.loads(lines[-1])
        except TimeoutError:
            logging.error("Timeout exceed in get_response_from_theb_ai")


class AdsURLGateway(PlayWrightCrawler):
    inputs: LinkedinURLData

    @property
    def data(self) -> List[LinkedinURLData]:
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    async def check_ads_id_exists(self, ads_id):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url + f"/api/ads/{ads_id}"
            )
            if response.status_code == 404:
                return ads_id

    @add_task(level=0)
    async def get_urls(
        self,
        page: Page,
        **_
    ):
        await page.goto(self.inputs.url)
        elements = await self.query_elements(
            page, "xpath=//div[@data-entity-urn]"
        )
        attributes = await asyncio.gather(
            *[element.get_attribute('data-entity-urn') for element in elements]
        )
        data_entities = [
            attribute.split("Posting:")[1]
            for attribute in attributes
        ]
        tasks = [
            self.check_ads_id_exists(ads_id)
            for ads_id in data_entities
        ]
        urls = await asyncio.gather(*tasks)
        results = [
            f"https://www.linkedin.com/jobs/view/{ads_id}"
            for ads_id in urls
            if ads_id
        ]
        self.data = [
            LinkedinURLData(
                url=url,
                country=self.inputs.country,
                job_mode=self.inputs.job_mode,
                ads_id=url.split("view/")[1]
            ) for url in results
        ]
