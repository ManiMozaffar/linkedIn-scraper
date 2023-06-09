JOB_ID = "(//div[@data-visible-time])[2]"
JOB_TOTAL_NUM = '//span[@class="results-context-header__job-count"]'
JOB_LI = '//div[@data-entity-urn]'
SHOW_MORE = '(//button[contains(text(), "Show more")])[1]'
BASE_SPAN = "(//h3[contains(@class, 'job-criteria-subheader')])/../span"
SENIORITY_LEVEL = f'({BASE_SPAN})[1]'
EMPLOYEMENT_TYPE = f'({BASE_SPAN})[2]'
BODY_INFO = '//div[contains(@class, "show-more-less-html__markup")]'
COMPANY_NAME = '//a[contains(@class, "name-link")]'
LOCATION = '//span[@class="topcard__flavor topcard__flavor--bullet"]'
JOB_ID_A_TAG = '//a[@class="topcard__link"]'
TITLE = '//h1'
NEED_LOGIN = '//*[contains(text(), "Already on Linkedin")]'


GPT_FILL = '//textarea[@class="n-input__textarea-el"]'
GPT_BUTTON = "//footer//button[@type and not(contains(@class, 'disabled'))]"
GPT_NEW_CHAT = '//*[contains(text(), "New chat")]'
