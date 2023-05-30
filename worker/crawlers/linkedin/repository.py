import requests
import asyncio
from typing import List
import json
import logging

from core.enums import HttpMethod
from crawlers.linkedin.gateway import AdsDataGateway, AdsURLGateway
from crawlers.linkedin.models import LinkedinURLData, LinkedinData
from crawlers.linkedin import utils, constants
from crawlers.repository import BaseRepository


class LinkedinRepository(BaseRepository):
    base_url = "http://127.0.0.1:8000"
    headless: bool

    async def get_url(self, inputs: List[LinkedinURLData]) -> AdsURLGateway:
        url_gateway = AdsURLGateway(
            inputs=inputs,
            proxy=utils.get_random_proxy(),
            finger_print_scipt=constants.SPOOF_FINGERPRINT,
            headless=self.headless,
            firefox_settings=constants.FIREFOX_SETTINGS
        )
        await url_gateway.execute()
        return url_gateway

    async def get_urls(
        self, inputs: List[LinkedinURLData]
    ) -> List[LinkedinURLData]:
        results: List[AdsURLGateway] = await self.gather_tasks(
            [self.get_url(input) for input in inputs]
        )
        _results = []
        for result in results:
            if result.data:
                _results.extend(result.data)
        return _results

    async def process_advertisement(
        self, inputs: AdsDataGateway
    ) -> LinkedinData:
        url_gateway = AdsDataGateway(
            inputs=inputs,
            proxy=utils.get_random_proxy(),
            finger_print_scipt=constants.SPOOF_FINGERPRINT,
            headless=self.headless,
            firefox_settings=constants.FIREFOX_SETTINGS
        )
        await url_gateway.execute()
        return url_gateway

    async def process_advertisements(
        self, inputs: List[AdsDataGateway]
    ) -> List[LinkedinData]:
        results: List[AdsDataGateway] = await self.gather_tasks(
            [self.process_advertisement(input) for input in inputs]
        )
        return [
            result.data for result in results
            if isinstance(result.data, LinkedinData)
        ]

    async def save_data_to_url(
        self, data: LinkedinData, endpoint: str, method: HttpMethod
    ) -> dict:
        response = requests.request(
            method=method.value.upper(),
            url=self.base_url + endpoint,
            json=json.loads(data.json())
        )
        if response.status_code == 200:
            logging.info("Saved data to URL")
        return response

    async def save_all_data(
        self, all_data: List[LinkedinData], endpoint: str, method: HttpMethod
    ):
        await asyncio.gather(
            *[
                self.save_data_to_url(data, endpoint, method)
                for data in all_data
            ]
        )
