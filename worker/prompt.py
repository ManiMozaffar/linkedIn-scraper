
def analyze_ads(company_name, job_description):
    return f"""
company_name = "{company_name}"
TASK = 'Simplify a job advertisement you find while job searching.'\n \n

WARNING! This is a sample output, it IS NOT THE ACTUAL JOB ADVERTISEMENT!!
-----------------------
job_description = '''
{job_description}
'''
-----------------------
sample_output = '''
Visa Sponsor: #Yes \n
• 3 years of experience with Delphi programming language \n
• Knowledge of Rest APIs, RemObjects SDK \n
'''
-----------------------
\n
INSTRUCTIONS:\n
1. Summarize hard skills or requiremenets from the `job_description` in a similiar format like `sample_output`, removing extra unnecessary details, list them as bullet points, max 70 characters each. DO not write more than 6 bullet point, only includes the MOST related and important one.\n
2. Translate non-English content to English. \n
3. Format visa sponsership as : `Visa Sponsor: #Yes, #No, or #NA`. \n
4. Check your 2021 database for the company's sponsorship status using `company_name`. Maybe in `job_description` this was mentioned, if  so give priority to `job_description`, if not then use your database \n
5. Provide a definite sponsorship status if possible, avoiding '#NA'. \n
6. Include programming languages in frameworks from `job_description`, if applicable. \n
7. Remember to not consider `sample_output` content as the actual job advertisement, for the acutal job advertisement, i have sent it to you as `job_description`  \n
----------- \n
\n

'''
"""


def get_tag_ads(title, job_description, keywords):
    sample = {
        "keywords": ["c_sharp", "dot_net", "backend"]
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
This is a list of keywords, that has {len(keywords)+1} keywords seperated with comma "," \n
KEYWORD_LIST = '''{str(keywords)}''' \n

`job_description`: '''
    {job_description} \n
\n '''


good_output = {str(good_sample)} \n
bad_output= {str(bad_sample)} \n
basic_sample = {str(sample)} \n

INSTRUCTIONS: \n
    1. I'm accessing you through a Python script and I need your response in a JSON string format. Make sure that you only send me this Json, with no other text, otherwise my program would have an exception and would not work perfect. Please make sure to ONLY respond using a JSON string and adhere to the format given as `basic_sample` which was menitoned earlier\n
    2. Consider `good_output` and `bad_output` and `basic_sample`  as just examples! The actual job advertisement is marked as `job_description` which you need to analyze and match accordingly.
    3. Do not stop writing answer unless you have at least included 5 different keyword/results, make sure they are REALLY RELEVANT, dont just write anything. Write at MAX 8 most related keywords, no more.\n 
    4. Read the `KEYWORD_LIST` that i have sent you at first. Read the `job_description` that have sent you. Check which of the provided `KEYWORD_LIST` are mentioned and required in `job_description`. \n
    5. Following step 4, Do not find keywords that do not exists in the given `KEYWORD_LIST` given at first, I only need matching KEYWORD LIST. Only include results from `KEYWORD_LIST` which I sent you at first \n
    6. Double check that keywords you've gathered in step 5 to be well-mentioned in the  `job_description` \n
    7. Double check that your gathered keyword from step 6 matches the exact spelling and case of the `KEYWORD_LIST` I provided as first, as `KEYWORD_LIST` are case-sensitive \n
    8. Analyze the job's title from `job_title` that is given to you before; match it with the most related job's name from `JOB_LISTS` list that I provided you at top or if none match, then label it as `others`. You must pick only 1 of the options. Include the result as a keywords following step 7\n
    9. Avoid the patterns of bad_output, follow the patterns of Good Output, when generating output.\n
    10. Rewrite a one paragraph short summary of the `job_description` so that you can understand it better. Add your rewritten text 3 lines after the json.
    """
