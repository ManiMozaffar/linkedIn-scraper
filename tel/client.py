from pyrogram import Client
from pyrogram import __version__
from pyrogram.raw.all import layer
import loguru

from env_reader import EnvReader


class LinkedinBot(Client):
    def __init__(self):
        envdata = EnvReader()
        super().__init__(
            str(envdata.api_id),
            api_id=envdata.api_id,
            api_hash=envdata.api_hash,
            bot_token=envdata.bot_token,
            workers=2,
            plugins=dict(root="plugins"),
        )

    async def start(self):
        await super().start()

        me = await self.get_me()
        loguru.logger.info(f"linkedIn-scraper on Pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")

    async def stop(self, *args):
        await super().stop()
        loguru.logger.info("linkedIn-scraper stopped. Bye.")


if __name__ == "__main__":
    LinkedinBot().run()
