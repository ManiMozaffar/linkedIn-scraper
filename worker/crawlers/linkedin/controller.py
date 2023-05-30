from itertools import product
import random
import asyncio

from loguru import logger


from crawlers.linkedin.repository import LinkedinRepository
from crawlers.linkedin.enums import JobModels
from crawlers.linkedin import constants, utils, models
from core.enums import HttpMethod


class LinkedinController:
    batch_size: int = 5

    def __init__(
        self, headless: bool, worker_num: int, is_popular: bool = True
    ):
        self.repository = LinkedinRepository(worker_num)
        self.repository.headless = headless
        self.is_popular = is_popular
        if self.is_popular:
            countries = constants.POPULAR_DESTINATION
        else:
            countries = constants.COUNTRIES
        job_urls = list(product(countries, utils.get_jobs(), JobModels))
        self.job_models = [
            models.LinkedinURLData(
                url=utils.get_url(job=job[1], mode=job[2], location=job[0]),
                country=job[0],
                job_mode=job[2]
            )
            for job in job_urls
        ]
        random.shuffle(self.job_models)

    async def process(self):
        for index in range(0, len(self.job_models), self.batch_size):
            batch = self.job_models[index:index+self.batch_size]
            logger.success(f"Processing {len(batch)} batches")
            ads_urls = await self.repository.get_urls(batch)
            logger.success(f"Fetched {len(ads_urls)} links")
            all_ads = await self.repository.process_advertisements(ads_urls)
            logger.success(f"Processed {len(ads_urls)} results")
            await self.repository.save_all_data(
                all_data=all_ads,
                endpoint="/api/ads/",
                method=HttpMethod.POST,
            )
            await asyncio.sleep(6)  # 6 second cooldown between each batch
