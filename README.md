# Playwright-LinkedIn-Scraper


## Table Of Contents
- [Overview](#overview)
- [Community](#community)
- [Features](#features)
- [How To Use](#how-to-use)
- [Installation](#installation)
- [Requirements](#requirements)
- [License](#license)
- [Support and Contributions](#support-and-contributions)
- [Legal](#legal)

## Proxycurl LinkedIn APIs

[![Proxycurl APIs enrich people and company profiles with structured data](https://raw.githubusercontent.com/josephlimtech/linkedIn-scraper/main/Proxycurl%20Logo.png)](https://nubela.co/proxycurl?utm_campaign=influencer_marketing&utm_source=github&utm_medium=social&utm_content=-mani_mozaffar)

Scrape public LinkedIn profile data at scale with [Proxycurl APIs](https://nubela.co/proxycurl?utm_campaign=influencer_marketing&utm_source=github&utm_medium=social&utm_content=-mani_mozaffar).

- Scraping Public profiles are battle tested in court in HiQ VS LinkedIn case.
- GDPR, CCPA, SOC2 compliant
- High rate limit - 300 requests/minute
- Fast - APIs respond in ~2s
- Fresh data - 88% of data is scraped real-time, other 12% are not older than 29 days
- High accuracy
- Tons of data points returned per profile

Built for developers, by developers.

## Overview

The Playwright-LinkedIn-Scraper is a tool that automates the process of collecting job postings, internships, and other opportunities from LinkedIn. It does this by using two powerful framework: Playwright and FastAPI. Playwright is a web automation tool that can navigate websites, click buttons, and scrape data from web pages. FastAPI is a web framework that allows for the creation of APIs in Python, which is the language used in this project.

The Playwright-LinkedIn-Scraper is customizable, meaning that you can filter the job postings you want to scrape based on your specific preferences. For example, you can search for job postings that match certain keywords or that are located in a specific city or country. If you want to customize the query parameters, you can do in the worker's directory.

After collecting the job postings, the Playwright-LinkedIn-Scraper can send them to a Telegram chat or channel of your choice. This allows you to share the job postings with your community or to keep track of them for your personal use. Overall, the Playwright-LinkedIn-Scraper is a powerful and flexible tool that can save you time and effort in your job search.


## Community
- [Telegram's Channel](https://t.me/linkedin_python)
- [Telegram's Bot](https://t.me/linkedin_python_bot)


## Features

1. **Advanced Browser Automation:** Uses Playwright to perform advanced browser automation and manipulation of LinkedIn's fingerprint.
2. **FastAPI Integration:** The FastAPI framework is used to build a lightweight, high-performance API to retrieve information quickly and efficiently.
3. **Customized Preferences:** The scraper allows you to filter results based on your customized preferences, such as location, job title, skills, or experience level.
4. **Telegram Integration:** The scraped data can be automatically sent to a Telegram chat or channel, making it easy to share with your community, track for personal use, or analyze.
5. **ChatGPT Analysis:** Uses ChatGPT to analyze the LinkedIn advertisement, and find the hard skills required from the job description, without having the overhead of using chatgpt API and instead used another chatgpt service provider to keep the running cost low.
6. **Translation**: Uses ChatGPT to translate the LinkedIn advertisement
7. **Visa Sponsership Analysis**: Uses chatgpt to analyse if the company sponsers visa or not.
8. **Telegram Bot Integration**: Uses telegram bot to alert users regarding their filter if they suit the job or not.
9. **Nested Logical Expression Filter Query**: And here's my favourite one, Ever wanted to buy a jerset set, as red and blue? but perhaps you couldn't filter the website by Red and blue, you could either do as red or blue, but here you can do nested logical expression. A use case would be for me indeed; the below filter will match the job, that is either django, fastapi or python has been mentioned as backend and also if fullstack with vuejs finds then it'd be still a match for me, and must be located inside netherlands or germany. Quite cool, innit?

```python 
(django or fastapi or python) and (netherlands or germany) and (backend or (fullstack and vuejs))
```

10. **Isolated Secure System To Evaluate Logical Expression** : Having this said, it's not a good practice to allow user inject python logical expression directly as input, but I guess I made it safe enough by seperating the endpoint for evaluation and some safety lookup before executing the code :) If you're still concerned about user's input, perhaps you can also use online consoles which comes with a fee, or use chatgpt api to analyse if the user's input is safe or not.



## How to use

- 1. First you need to join the telegram's channel and start telegram's bot.
- 2. Then you need to setup your own filter, according to your needs, simply send it as a text message to bot, here's one sample:
    ```python 
    (django or fastapi or python) and (netherlands or germany) and (backend or (fullstack and vuejs))
    ```
    this is either django, fastapi or python has been mentioned as backend and also if fullstack with vuejs finds then it'd be still a match for me, and must be located inside netherlands or germany. Quite cool, innit?
- 3. Verify that your filter is alright by sending /info to the bot
- 4. Drink your ☕, and wait for the bot to send you latest advertisements according to your filter 🚀

## Installation

To run the project
1. Create a .env file containing secret key, database information, telegram token and the chat id you want send messages to. 
2. run the docker build and up command to run the service
3. Add some proxies to the database using endpoint, and jobs, and keywords. For keywords you can use the loaddata in keyword's service
4. Run the worker's main.py. For some reasons I decided to not run playwright in docker. Use `w` for concurrency of data mining, use --headless if you wish to run browser in headless, and use -p if you wish to only scrap popular countries.
```python
python main.py -w 5 --headless
```
5. Start the bot's token_id you gave at top, and insert the boolean expression that you wish to be used


## Requirements

1. Few HTTP Proxy
2. Docker installed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support and Contributions

Please open an issue for any questions, bug reports, or feature requests. Contributions are welcome, and we encourage you to submit a pull request with any improvements or additions.

## Legal

Please note that the following code is not affiliated with, authorized, maintained, sponsored or endorsed by LinkedIn or any of its affiliates or subsidiaries. This is an independent and unofficial project and should be used at your own risk.
This project is using guest account view and proxy, but we are not responsible for any consequences that may arise from the use of this project.
