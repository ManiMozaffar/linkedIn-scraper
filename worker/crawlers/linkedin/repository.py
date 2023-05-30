import aiohttp
import asyncio
from typing import List
import json
from loguru import logger

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
        self, session: aiohttp.ClientSession,
        data: LinkedinData, endpoint: str, method: HttpMethod
    ) -> dict:
        try:
            async with session.request(
                method=method.value.upper(),
                url=self.base_url + endpoint,
                json=json.loads(data.json())
            ) as response:
                if response.status == 200:
                    logger.info("Saved data to URL")
                return await response.json()
        except Exception as error:
            logger.error(f"Error saving data to URL: {error}")

    async def save_all_data(
        self, all_data: List[LinkedinData], endpoint: str, method: HttpMethod
    ):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[
                    asyncio.ensure_future(
                        self.save_data_to_url(session, data, endpoint, method)
                    )
                    for data in all_data
                ]
            )
