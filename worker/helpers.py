import random
from urllib.parse import urlencode
import functools
from itertools import product
import argparse

from playwright.async_api import (
    Page,
    TimeoutError as PlayWrightTimeOutError
)
import requests
from playwright._impl._api_structures import ProxySettings

import constants
import exceptions
import decorators
import enums


def format_country(country):
    return country.lower().replace(" ", "_")


def get_jobs():
    resp: dict = requests.get(
        "http://127.0.0.1:8000/api/jobs?page=1&per_page=1000"
    ).json()
    job_list = list(map(
        lambda x: x['name'], resp['results']
    )) if resp.get('results') else None

    if not job_list:
        raise exceptions.NoJobException(
            "Please add some jobs to API"
        )
    return job_list


@decorators.get_unique_object
def get_country_and_job(is_popular=False):
    if is_popular:
        countries = constants.POPULAR_DESTINATION
    else:
        countries = constants.COUNTRIES

    return list(product(
        countries, get_jobs(), enums.JobModels
    ))


def get_url(job: str, mode: enums.JobModels, page_number=0, location=None):
    """
    Builds URL Parameter for LinkedIn.

    Args:
        page_number (int, optional): The page number to fetch. Defaults to 0.
        location (str, optional): The location to search for jobs. Defaults to
        None.
        mode: Enum mode for the job

    Returns:
        str: The LinkedIn URL with the given parameters.
    """
    url = "https://www.linkedin.com/jobs/search"
    params = {
        "keywords": job,
        "location": location,
        "trk": "public_jobs_jobs-search-bar_search-submit",
        "position": 1,
        "pageNum": page_number,
        "f_TPR": "r10800",
        "f_JT": "F",
        "f_WT": mode.value
    }
    query_params = urlencode(params)
    return f"{url}?{query_params}"


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


async def get_element_text(page: Page, xpath: str, replace=True, timeout=None):
    """
    Get the text content of an element using its XPath.

    Args:
        page (Page): The Page object to search for the element.
        xpath (str): The XPath of the element.
        replace (bool, optional): Whether to remove newlines and trailing
        whitespace from the text. Defaults to True.
        timeout (int, optional): The maximum time to wait for the element.
        Defaults to None.

    Returns:
        str: The text content of the element.
    """
    result: str = await page.locator(xpath).text_content(timeout=timeout)
    if replace:
        return result.strip().replace("\n", "")
    else:
        return result


async def fill_form(page: Page, xpath: str, text: str, timeout=None):
    """
    Fill a form field with the given text using its XPath.

    Args:
        page (Page): The Page object containing the form field.
        xpath (str): The XPath of the form field.
        text (str): The text to fill into the form field.
        timeout (int, optional): The maximum time to wait for the form field.
        Defaults to None.

    Returns:
        None
    """
    return await page.locator(xpath).fill(text, timeout=timeout)


@decorators.exception_handler
async def safe_get_element_text(page: Page, xpath: str, replace=True, timeout=None):
    """
    Safely get the text content of an element using its XPath.

    Args:
        page (Page): The Page object to search for the element.
        xpath (str): The XPath of the element.
        replace (bool, optional): Whether to remove newlines and trailing
        whitespace from the text. Defaults to True.
        timeout (int, optional): The maximum time to wait for the element.
        Defaults to None.

    Returns:
        str: The text content of the element, or an empty string on failure.
    """
    return await get_element_text(page, xpath, replace, timeout=timeout)


@decorators.exception_handler
async def safe_fill_form(page: Page, xpath: str, text: str, timeout=None):
    """
    Safely fill a form field with the given text using its XPath.

    Args:
        page (Page): The Page object containing the form field.
        xpath (str): The XPath of the form field.
        text (str): The text to fill into the form field.
        timeout (int, optional): The maximum time to wait for the form field.
        Defaults to None.

    Returns:
        None
    """
    return await fill_form(page, xpath, text, timeout=timeout)


async def does_element_exists(
        page: Page, xpath: str, timeout: int = 500
):
    try:
        await page.locator(xpath).wait_for(timeout=timeout)
        return True
    except PlayWrightTimeOutError:
        return False


def does_ads_exists(ads_id) -> bool:
    """
    Check if an advertisement already exists in the database.

    :param ads_id: Advertisement ID to check for existence.
    :return: True if advertisement exists, False otherwise.
    """
    return requests.get(f"{constants.HOST}/api/ads/{int(ads_id)}").status_code == 200


def create_proxy_url(proxy_dict: dict) -> ProxySettings:
    """
    Create a proxy URL from the given proxy dictionary.

    :param proxy_dict: Dictionary containing proxy information.
    :return: A ProxySettings object with the proxy details.
    """
    return ProxySettings(
        server=f"http://{proxy_dict['ip_address']}:{proxy_dict['port']}",
        username=proxy_dict['username'], password=proxy_dict['password']
    )


def get_random_proxy() -> ProxySettings:
    """
    Get a random proxy from the available proxy list.

    :return: A ProxySettings object with a random proxy's details.
    """
    proxy_dict = requests.get(
        f"{constants.HOST}/api/proxy?order_by=?&page=1&per_page=1"
    ).json()["results"]
    if proxy_dict is None or len(proxy_dict) == 0:
        raise exceptions.NoProxyException("Please Add A Proxy")
    return create_proxy_url(proxy_dict[0])


@functools.lru_cache(maxsize=128)
def get_all_keywords(cached=0) -> list:
    return requests.get(
        "http://127.0.0.1:8000/api/tech/keywords"
    ).json()["result"]


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
