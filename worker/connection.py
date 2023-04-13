import requests

host = "http://127.0.0.1:8000"


def create_ads(
        ads_id, location, body, company_name, title, source, employement_type,
        level, country
):
    data = {
        "ads_id": ads_id,
        "location": location,
        "country": country,
        "body": body,
        "company_name": company_name,
        "title": title,
        "source": source,
        "employement_type": employement_type,
        "level": level
    }
    resp = requests.post(f"{host}/api/ads", json=data)
    if resp.status_code != 200:
        print(resp.text)
