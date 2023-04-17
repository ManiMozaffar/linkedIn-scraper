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
    "keywords": ["python", "django", "...."]
}


TAG_ADS = f"""


Hey ChatGPT!
I'm accessing you through a Python script and I need your response in a JSON string format. Please make sure to ONLY respond using a JSON string and adhere to the following format:
{str(SAMPLE)}


INSTRUCTIONS:
1. Read the advertisement and identify any MATCHING keywords from the provided list. Please note that I have already sent you the advertisement and the list of keywords in this message as above.
2. Include the matching keywords in your JSON string response using the key 'keywords'.
3. Use the exact spelling and case of the keywords provided as earlier, they are case-sensitive.
4. Analyze the keywords carefully, as some may have been renamed to respect Python's namespacing rules (e.g., "c#" to "c_sharp" or ".NET" to "dot_net"). Only include the EXACT MATCHING keywords in your response.
5. If you find a keyword in the advertisement that is not in the provided list, ignore it. do not mention it in your response.
"""
