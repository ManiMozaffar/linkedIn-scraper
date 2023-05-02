import asyncio
import random

from scraper import linkedin
import helpers


async def run_scrapers(workers: int = 1, only_popular=False, headless=True):
    while True:
        tasks = []
        for i in range(workers):
            tasks.append(asyncio.create_task(linkedin.scrape_linkedin(
                worker_id=i+1, only_popular=only_popular, headless=headless
            )))
            await asyncio.sleep(random.randint(1, 3))  # Overhead of browsers
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    args = helpers.parse_arguments()
    used_countries = asyncio.run(run_scrapers(
        workers=args.workers, only_popular=args.popular,
        headless=args.headless
    ))
