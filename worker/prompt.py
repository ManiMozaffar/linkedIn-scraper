ANALYZE_ADS = """

TASK:
Simplify a job advertisement you find while job searching.\n \n

This is a sample output, it IS NOT THE ACTUAL JOB ADVERTISEMENT.\n
-----------------------
SAMPLE OUTPUT:

Visa Sponsor: #Yes

• 3 years of Django experience
• Knowledge of RESTful APIs, Django Rest Framework
-----------------------
\n
INSTRUCTIONS:\n
1. Summarize hard skills from the `Job Description`, removing extra unnecessary details, list them as bullet points, max 70 characters each\n
2. Translate non-English content to English. \n
3. Show the company's visa sponsorship status: #Yes, #NA, or #No. \n
4. Format: `Visa Sponsor: #Yes, #No, or #NA`. \n
5. Check your 2021 database for the company's sponsorship status. Maybe in `Job Description` this was mentioned, so give priority to `Job Description` than your database \n
6. Provide a definite sponsorship status if possible, avoiding '#NA'. \n
7. Include programming languages in frameworks from `Job Description`, if applicable. \n
8. Remember to not consider `SAMPLE OUTPUT` as the actual job advertisement, which i will send you as `Job Description` below \n
----------- \n
Job Description (The Real INPUT): \n
"""

SAMPLE = {
    "keywords": ["python", "django", "backend"]
}

GOOD_SAMPLE = {
    "keywords": ["backend", "germany", "dot_net", "c_sharp"]
}

BAD_SAMPLE = {
    "keywords": ["back end", "Germany", ".NET", "C#"]
}


TAG_ADS = f"""
INSTRUCTIONS: \n
1. I'm accessing you through a Python script and I need your response in a JSON string format. Make sure that you only send me this Json, with no other text, otherwise my program would have an exception and would not work perfect. Please make sure to ONLY respond using a JSON string and adhere to the following format: \n
{str(SAMPLE)}
\n
2. Read the KEYWORDS_LIST that i have sent you at first. Read the advertisement that I'll send you in below. Check which of the provided KEYWORDS_LIST are mentioned and required in advertisement. \n
3. Following step2, Do not find keywords that do not exists in the given KEYWORDS_LIST given at first, I only need matching KEYWORD LIST. Only include results from KEYWORDS_LIST which I sent you at first \n
4. Double check that keywords you've gathered in step 3 to be well-mentioned in the  advertisement
5. Double check that your gathered keyword from step4 matches the exact spelling and case of the KEYWORDS_LIST I provided as first, as KEYWORDS_LIST are case-sensitive \n
6. Do not stop writing answer unless you have at least included 5 different keyword/results, make sure they are REALLY RELEVANT, dont just write anything.\n 
7. Analyze the job from job title, and match it with: `backend` `frontend` `devops` `software` `full_stack` `data_science` `network_engineering` `cybersecurity` or if none match, then label it as `others` \n
8. Avoid the patterns of Bad Output, follow the patterns of Good Output. \n
Good Output: {str(GOOD_SAMPLE)} \n
Bad Output: {str(BAD_SAMPLE)} \n
"""
