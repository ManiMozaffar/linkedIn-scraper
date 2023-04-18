ANALYZE_ADS = """

TASK:
Imagine you are job searching and come across a job advertisement.
Your task is to simplify the advertisement.

-----------------------
GOOD OUTOUT:

Sponsor Status: #Yes

• Django
• RESTful APIs
-----------------------
BAD OUTPUT:

Sponsor Status: #NA

• Strong proficiency in Django framework with a minimum of 3 years of experience in building web applications with it.
• Strong understanding and experience in building RESTful APIs using Django Rest Framework.
-----------------------

INSTRUCTIONS:
1. Extract and list the required hard skills for the job from the advertisement in a concise and summarized format.
2. Translate any non-English content to English.
3. Indicate the company's visa sponsorship status in the second line of your response using one of these options: #Yes for sponsorship, #NA if unsure, and #No if no sponsorship.
4. Use your 2021 database to search for the company's name to determine their sponsorship status.
5. Provide a definite sponsorship status whenever possible, avoiding 'N/A'.
6. Include programming languages used in frameworks that mentioned in advertisement, if applicable.
7. Follow the formatting and style of the "GOOD OUTPUT EXAMPLE" provided and avoid the patterns of the "BAD OUTPUT EXAMPLE".
8. Present hard skills as bullet points with no more than 70 characters each.
9. Do not include any details other than those present in the GOOD OUTPUT EXAMPLE.

-----------
Job Description(INPUT):
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
I'm accessing you through a Python script and I need your response in a JSON string format. Please make sure to ONLY respond using a JSON string and adhere to the following format: \n
{str(SAMPLE)}
\n
INSTRUCTIONS: \n
1. Read the keywords that i have sent you previously on top of this text. Read the advertisement that I'll send you in below. Detect the matching keywords with keywords I have sent you at first.\n
2. Analyze the job from job title, and match it with: `backend` `frontend` `devops` `software` `full_stack` or if none match, then label it as `others` \n
3. DO NOT CREATE KEYWORDS ON YOUR OWN. ONLY use the provided list of KEYWORDS \n
4. Use the exact spelling and case of the KEYWORDS provided, as they are case-sensitive. \n
5. Analyze the KEYWORDS I have sent you carefully. They usually follow python's namespacing rules. (e.g., "c#" to "c_sharp" or ".NET" to "dot_net"). Use the version of keyword I have provided for you \n
6. If you find a keyword in the advertisement that is not in the provided list, ignore it. Do not write it in your response. Only include results from KEYWORDS i sent you above. \n
Good Output: {str(SAMPLE)} \n
Bad Output: {str(BAD_SAMPLE)} \n
7. Avoid the patterns of Badoutput, follow the patterns of Good Output. \n
8. Do not stop writing answer unless you have at least included 6 different keyword, with the matching job and country as requested before \n 
"""
