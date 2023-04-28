
def analyze_ads(company_name, job_description):
    return f"""
company_name = "{company_name}"
TASK = 'Simplify a job advertisement you find while job searching.'\n \n

WARNING! This is a sample output, it IS NOT THE ACTUAL JOB ADVERTISEMENT!!
-----------------------
sample_output = '''
Visa Sponsor: #Yes

• 3 years of experience with Delphi programming language
• Knowledge of Rest APIs, RemObjects SDK
'''
-----------------------
\n
INSTRUCTIONS:\n
1. Summarize hard skills or requiremenets from the `job_description`, removing extra unnecessary details, list them as bullet points, max 70 characters each. DO not write more than 6 bullet point, only includes the MOST related and important one.\n
2. Translate non-English content to English. \n
3. Format visa sponsership as : `Visa Sponsor: #Yes, #No, or #NA`. \n
4. Check your 2021 database for the company's sponsorship status using `company_name`. Maybe in `job_description` this was mentioned, if  so give priority to `job_description`, if not then use your database \n
5. Provide a definite sponsorship status if possible, avoiding '#NA'. \n
6. Include programming languages in frameworks from `job_description`, if applicable. \n
7. Remember to not consider `sample_output` as the actual job advertisement, for the acutal job advertisement, i will send it to you as `job_description` in few lines below \n
----------- \n
\n
job_description = '''
{job_description}
'''
"""


def get_tag_ads(title, job_description, keywords):
    sample = {
        "keywords": ["python", "django", "backend"]
    }
    good_sample = {
        "keywords": ["backend", "germany", "dot_net", "c_sharp"]
    }
    bad_sample = {
        "keywords": ["back end", "Germany", ".NET", "C#"]
    }
    return f"""
TASK =  "Read the the text, then follow up the instructions that is given at the end."
job_title = "{title}"\n

JOB_LISTS = `["backend", "frontend", "devops", "full_stack", "data_science", "machine_learning", "network_engineering", "cybersecurity"]` \n
This is a list of keywords, that has {len(keywords)} index \n
KEYWORDS_LIST = '''{keywords}''' \n

`job_description`: \n
    {job_description} \n
\n

INSTRUCTIONS: \n
    1. I'm accessing you through a Python script and I need your response in a JSON string format. Make sure that you only send me this Json, with no other text, otherwise my program would have an exception and would not work perfect. Please make sure to ONLY respond using a JSON string and adhere to the following format: \n
    `SAMPLE` = {str(sample)}
    \n
    2. Read the `KEYWORDS_LIST` that i have sent you at first. Read the `job_description` that have sent you. Check which of the provided `KEYWORDS_LIST` are mentioned and required in `job_description`. \n
    3. Following step2, Do not find keywords that do not exists in the given `KEYWORDS_LIST` given at first, I only need matching KEYWORD LIST. Only include results from `KEYWORDS_LIST` which I sent you at first \n
    4. Double check that keywords you've gathered in step 3 to be well-mentioned in the  `job_description`
    5. Double check that your gathered keyword from step4 matches the exact spelling and case of the `KEYWORDS_LIST` I provided as first, as `KEYWORDS_LIST` are case-sensitive \n
    6. Do not stop writing answer unless you have at least included 5 different keyword/results, make sure they are REALLY RELEVANT, dont just write anything. Write at max 10 related ones. Include the most important ones only.\n 
    7. Analyze the job from `job_title` and `job_description`, and match it with `JOB_LISTS` list that I provided you at top or if none match, then label it as `others`. You may even pick more than 1 in some cases\n
    8. Avoid the patterns of bad_output, follow the patterns of Good Output, when generating output.\n
    `good_output` = {str(good_sample)} \n
    `bad_output`= {str(bad_sample)} \n
    9. Consider `good_output` and `bad_output` and `SAMPLE`  as just examples! The actual job advertisement is marked as `job_description` which you need to analyze.
    10. Rewrite a summary of the `job_description` so that you can understand it better. Add your rewritten text 3 lines after the json.
    """
