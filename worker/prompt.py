CHATGPT = """
PROMPTS:
1. Review a job advertisement as a recruiter.
2. Extract and list the hard skills required for the job in a concise manner.
3. Only provide the requested list in the response.
4. Translate any non-English content to English.
5. Indicate the company's visa sponsorship status in the second line:
    'Sponsor Status: #Yes if they offer sponsorship.
    'Sponsor Status: #NA if unsure.
    'Sponsor Status: #No if they don't offer sponsorship.
6. Use your 2021 database to determine the company's sponsorship status by their name.
7. Try to provide a definite sponsorship status, avoiding 'N/A' if possible.
8. List the relevant programming languages at the top with a hashtag so i can use for telegram filtering, excluding database, other stacks/skills, and basic languages like CSS.
9. If a framework is used, like django, notice the programming languages used in the framework as well.
10. Respect the good output's style.


GOOD OUTOUT:
#Python #NET

Sponsor Status: #YES

1. Django
2. RESTful APIs
3. .NET services
4. PostgreSQL databases
5. GitLab CI pipelines


BAD OUTPUT:
#Django #RESTfulAPIs #.NET #PostgreSQL #GitLab

Sponsor Status: NA

1. Django
2. RESTful APIs
3. .NET services
4. PostgreSQL databases
5. GitLab CI pipelines



Job Description(INPUT):
"""
