import random
from typing import Any

import pytz
from playwright.async_api import (
    Page,
    BrowserContext,
    async_playwright
)

from core.base import BaseTaskEngine
from pydantic import BaseModel


class PlayWrightCrawler(BaseTaskEngine):

    def __init__(
        self,
        proxy,
        headless,
        firefox_settings,
        finger_print_scipt,
        inputs: BaseModel,
        *args, **kwargs
    ):
        self.inputs = inputs
        self.proxy = proxy
        self.headless = headless
        self.firefox_settings = firefox_settings
        self.finger_print_scipt = finger_print_scipt
        self._data = None
        super().__init__(*args, **kwargs)

    async def setup(self) -> dict:
        async_manager = async_playwright()
        driver = await async_manager.start()
        browser = await driver.firefox.launch(
            headless=self.headless,
            args=[
                '--start-maximized',
                '--foreground',
                '--disable-backgrounding-occluded-windows'
            ],
            firefox_user_prefs=self.firefox_settings
        )
        context = await browser.new_context(
            timezone_id=random.choice(pytz.all_timezones),
            accept_downloads=True,
            is_mobile=False,
            has_touch=False,
            proxy=self.proxy
        )
        page = await context.new_page()
        await page.bring_to_front()

        if self.finger_print_scipt:
            await page.add_init_script(
                self.finger_print_scipt
            )
        return {
            "browser": browser,
            "page": page,
            "async_manager": async_manager
        }

    async def tear_down(
        self, browser: BrowserContext, async_manager: async_playwright, **_
    ):
        await browser.close()
        await async_manager.__aexit__()
        return None

    async def base_action(
        self,
        page: Page,
        xpath,
        raise_error,
        timeout,
        action,
        **kwargs
    ) -> Any:
        try:
            result: str = await getattr(
                page.locator(xpath), action
            )(
                timeout=timeout, **kwargs
            )
            return result

        except Exception as error:
            if raise_error:
                raise error from None
            return None

    async def click_xpath(
        self,
        page: Page,
        xpath,
        raise_error: bool = False,
        timeout: int = 5_000
    ):
        return await self.base_action(
            page, xpath, raise_error, timeout, action="click",
        )

    async def read_from_xpath(
        self,
        page: Page,
        xpath,
        raise_error: bool = False,
        timeout: int = 2_000
    ):
        return await self.base_action(
            page, xpath, raise_error, timeout, action="text_content",
        )

    async def get_all_elements(
        self,
        page: Page,
        xpath,
        raise_error: bool = False,
        timeout: int = 5_000
    ):
        return await self.base_action(
            page, xpath, raise_error, timeout, action="all",
        )

    async def fill_form(
        self,
        page: Page,
        xpath,
        raise_error: bool = False,
        timeout: int = 5_000,
        text: str = None
    ):
        return await self.base_action(
            page, xpath, raise_error, timeout, action="fill",
            value=text
        )

    async def query_elements(
        self,
        page: Page,
        query: str
    ):
        return await page.query_selector_all(query)
