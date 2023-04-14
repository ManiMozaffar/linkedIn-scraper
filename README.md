# Playwright-LinkedIn-Scraper


## Overview
The Playwright-LinkedIn-Scraper is a tool that automates the process of collecting job postings, internships, and other opportunities from LinkedIn. It does this by using two powerful framework: Playwright and FastAPI. Playwright is a web automation tool that can navigate websites, click buttons, and scrape data from web pages. FastAPI is a web framework that allows for the creation of APIs in Python, which is the language used in this project.

The Playwright-LinkedIn-Scraper is customizable, meaning that you can filter the job postings you want to scrape based on your specific preferences. For example, you can search for job postings that match certain keywords or that are located in a specific city or country. If you want to customize the query parameters, you can do in the worker's directory.

After collecting the job postings, the Playwright-LinkedIn-Scraper can send them to a Telegram chat or channel of your choice. This allows you to share the job postings with your community or to keep track of them for your personal use. Overall, the Playwright-LinkedIn-Scraper is a powerful and flexible tool that can save you time and effort in your job search.



## Features
1. **Advanced Browser Automation:** Uses Playwright to perform advanced browser automation and manipulation of LinkedIn's fingerprint.
2. **FastAPI Integration:** The FastAPI framework is used to build a lightweight, high-performance API to retrieve information quickly and efficiently.
3. **Customized Preferences:** The scraper allows you to filter results based on your customized preferences, such as location, job title, skills, or experience level.
4. **Telegram Integration:** The scraped data can be automatically sent to a Telegram chat or channel, making it easy to share with your community, track for personal use, or analyze.
5. **ChatGPT Analysis:** Uses ChatGPT to analyze the LinkedIn advertisement, and find the hard skills required from the job description, without having the overhead of using chatgpt API and instead used another chatgpt service provider to keep the running cost low.


## Installation

To run the project
1. Create a .env file containing secret key, database information, telegram token and the chat id you want send messages to. 
2. run the docker build and up command to run the service
3. Add some proxies to the database
4. Run the worker's main.py. For some reasons I decided to not run playwright in docker.


## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support & Contributions
Please open an issue for any questions, bug reports, or feature requests. Contributions are welcome, and we encourage you to submit a pull request with any improvements or additions.
