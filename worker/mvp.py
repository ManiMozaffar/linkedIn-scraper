from crawlers.linkedin import LinkedinController
import asyncio


async def service(
    headless: bool = False,
    worker_num: int = 5,
    is_popular: bool = True
):
    obj = LinkedinController(
        headless=headless,
        worker_num=worker_num,
        is_popular=is_popular
    )
    await obj.process()


if __name__ == "__main__":
    asyncio.run(service())
