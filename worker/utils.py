import random
from urllib.parse import urlencode

COUNTRIES = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Greece",
    "Czech Republic", "Denmark", "Estonia", "Finland", "France",
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
