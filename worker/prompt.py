CHATGPT = """
PROMPTS:
1. Imagine you are looking for a job and you come across a job advertisement. Your task is to review the advertisement.
2. From the job advertisement, extract and list the technical skills required for the job in a short and concise format.
3. Provide only the requested list of technical skills in your response.
4. If there is any content in a language other than English, translate it to English.
6. Indicate whether the company offers visa sponsorship in the second line of your response. Use one of these three options: #Yes if they offer sponsorship, #NA if you are unsure, and #No if they do not offer sponsorship.
7. To determine the company's sponsorship status, use your 2021 database to search for the company's name.
8. Try to provide a definite sponsorship status, avoiding 'N/A' if possible.
9. At the top of your response, list the relevant programming languages as hashtags, which will enable users to filter by language on Telegram. Exclude any databases, other technology stacks/skills, and basic languages like CSS.
10. If a framework like Django is used, include the programming languages used in that framework as well.
11. Please follow the formatting style and patterns of the "GOOD OUTPUT" example provided and avoid patterns of "BAD OUTPUT" example
12. Write hardskill as bulletpoints, and Don't write more than 70 Characters in each bulletpoint.
13. Don't add any details other than the one exists in GOOD OUTPUT.
-----------------------
GOOD OUTOUT:
#Python #NET

Sponsor Status: #YES

• Django
• RESTful APIs
• .NET services
• PostgreSQL databases
• GitLab CI pipelines

-----------------------
BAD OUTPUT:
#Django #RESTfulAPIs #.NET #PostgreSQL #GitLab

Sponsor Status: #NA

• Strong proficiency in Django framework with a minimum of 3 years of experience in building web applications with it.
• Strong understanding and experience in building RESTful APIs using Django Rest Framework.
• Proficient in developing .NET services with a minimum of 3 years of experience in the field.
• Strong experience in working with PostgreSQL databases, including creating and maintaining schemas, and writing complex queries.
• Strong experience in setting up and configuring GitLab CI pipelines for continuous integration and deployment.
• Excellent analytical and time management skills with the ability to work effectively in a team environment.
• Native or excellent knowledge of English, both written and spoken.
-----------------------


Job Description(INPUT):
"""
