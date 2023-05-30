import asyncio

from core.utils import parse_arguments
from mvp import service


if __name__ == "__main__":
    args = parse_arguments()
    while True:
        used_countries = asyncio.run(
            service(
                worker_num=args.workers,
                is_popular=args.popular,
                headless=args.headless
            )
        )
