from urllib.parse import urlencode
import functools
import re
import json
from typing import Tuple

import requests
from playwright._impl._api_structures import ProxySettings
import loguru

from crawlers.linkedin import enums, constants
import exceptions


def process_thebai_responses_to_text(
    first_resp, second_resp, country, job_mode
) -> Tuple[str, str]:
    if not validate_thebai_response(first_resp):
        return (None, None)  # This will raise an exception in pydantic :)

    if not validate_thebai_response(second_resp):
        return (first_resp["text"], None)

    body = first_resp["text"]
    second_resp_tags = None
    try:
        second_resp_text = re.search(
            r'\{.*\}', second_resp["text"].replace("'", "\"")
        )
        if not second_resp_text:
            raise exceptions.NoJsonFound(
                "No valid JSON object found in the last line"
            )
        second_resp_text = second_resp_text.group()
        second_resp_tags: list = json.loads(second_resp_text)["keywords"]
        if "#YES" in first_resp["text"].upper():
            second_resp_tags.append("yes")
        elif "#NO" in first_resp["text"].upper():
            second_resp_tags.append("no")
        else:
            second_resp_tags.append("na")
        second_resp_tags.extend([job_mode, country])
        hashtags = ' '.join(set(f"#{tag}" for tag in second_resp_tags))
        body = f"""{first_resp["text"]}
            {hashtags}
        """
    except (json.JSONDecodeError, KeyError, ValueError) as error:
        loguru.logger.error(
            f"Error happened parsing responses from thebai: {error}"
        )
    finally:
        return (body, second_resp_tags)


def validate_thebai_response(response):
    for item in constants.IGNORE_LIST:
        if item.lower() in response["text"]:
            return False
    return True


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
def get_all_keywords() -> list:
    return requests.get(
        "http://127.0.0.1:8000/api/tech/keywords"
    ).json()["result"]
