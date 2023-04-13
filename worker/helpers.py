import random
from urllib.parse import urlencode
from playwright.async_api import Page
from functools import wraps
import traceback

COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Greece",
    "Czechia", "Denmark", "Estonia", "Finland", "France",
    "Germany", "Hungary", "Ireland", "Italy", "Netherlands",
    "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
    "United States", "Canada", "Australia", "New Zealand", "Japan",
    "South Korea", "Singapore"
]


def get_location():
    return random.choice(COUNTRIES)


def get_url(page_number=0):
    url = "https://www.linkedin.com/jobs/search"
    params = {
        "keywords": "Python Backend",
        "location": get_location(),
        "trk": "public_jobs_jobs-search-bar_search-submit",
        "position": 1,
        "pageNum": page_number,
        "f_TPR": "r86400"
    }
    query_params = urlencode(params)
    return f"{url}?{query_params}"


def generate_device_specs():
    random_ram = random.choice([1, 2, 4, 8, 16, 32, 64])
    max_hw_concurrency = random_ram * 2 if random_ram < 64 else 64
    random_hw_concurrency = random.choice([1, 2, 4, max_hw_concurrency])
    return (random_ram, random_hw_concurrency)


async def get_element_text(page: Page, xpath: str, replace=True):
    result: str = await page.locator(xpath).text_content()
    if replace:
        return result.strip().replace("\n", "")
    else:
        return result


def exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred in function {func.__name__} with {args} & {kwargs}: {e}")
            traceback.print_exc()
            return ""
    return wrapper


@exception_handler
async def safe_get_element_text(page: Page, xpath: str, replace=True):
    return await get_element_text(page, xpath, replace)
