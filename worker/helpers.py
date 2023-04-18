import random
import time
import traceback
from urllib.parse import urlencode
from functools import wraps


from playwright.async_api import Page
import loguru
import requests
from playwright._impl._api_structures import ProxySettings


import constants
import exceptions


def format_country(country):
    return country.lower().replace(" ", "_")


def get_country(used: list):
    """
    Get a country from COUNTRIES list that has not been used before.

    Args:
        used (list): A list of countries already used.

    Returns:
        Tuple[str, list]: A tuple containing a random country from the list
        and a new used list.
    """
    if len(used) != len(constants.COUNTRIES):
        random.shuffle(constants.COUNTRIES)
        result = next((
            country for country in constants.COUNTRIES if country not in used),
            None
        )
        used.append(result)
        loguru.logger.info(
            f"Total Country Left: {len(constants.COUNTRIES)-len(used)}"
        )
        return (result, used)
    else:
        used.clear()
        loguru.logger.info("Sleeping for 30 minutes as all countries finished")
        time.sleep(30*60)
        return get_country(used)


def get_random_job():
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
    return random.choice(job_list)


def get_url(page_number=0, location=None):
    """
    Builds URL Parameter for LinkedIn.

    Args:
        page_number (int, optional): The page number to fetch. Defaults to 0.
        location (str, optional): The location to search for jobs. Defaults to
        None.

    Returns:
        str: The LinkedIn URL with the given parameters.
    """
    url = "https://www.linkedin.com/jobs/search"
    params = {
        "keywords": get_random_job(),
        "location": location,
        "trk": "public_jobs_jobs-search-bar_search-submit",
        "position": 1,
        "pageNum": page_number,
        "f_TPR": "r86400",
        "sortBy": "DD",
        "f_JT": "F"
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


def exception_handler(func):
    """
    Decorator that handles exceptions and returns an empty string on failure.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """
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


@exception_handler
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


def get_all_keywords() -> list:
    return requests.get(
        "http://127.0.0.1:8000/api/tech/keywords"
    ).json()["result"]
