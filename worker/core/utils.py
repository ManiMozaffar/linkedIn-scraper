import argparse
import random


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-w", "--workers", type=int, default=1,
        help="Number of workers to run."
    )
    parser.add_argument(
        "-p", "--popular", action="store_true",
        help="Scrape only popular countries."
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Enable headless mode."
    )
    args = parser.parse_args()
    return args


def generate_device_specs():
    """
    Generate random RAM/Hardware Concurrency.

    Returns:
        Tuple[int, int]: A tuple containing a random RAM and hardware
        concurrency.
    """
    random_ram = random.choice([1, 2, 4, 8, 16, 32, 64])
    max_hw_concurrency = random_ram * 2 if random_ram < 64 else 64
    random_hw_concurrency = random.choice([1, 2, 4, max_hw_concurrency])
    return (random_ram, random_hw_concurrency)
