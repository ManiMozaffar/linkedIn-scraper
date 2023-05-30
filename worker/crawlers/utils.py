import random


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
