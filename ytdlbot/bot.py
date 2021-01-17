import shutil

from pyrogram import Client

from ytdlbot.config import Config
from ytdlbot import LOGGER


class YtDLBot(Client):
    def __init__(self):
        name = self.__class__.__name__.lower()

        plugins = dict(root=f"{name}/plugins")
        super().__init__(
            session_name=":memory:",
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=100,
            plugins=plugins
        )

    async def start(self):
        await super().start()
        bot = await self.get_me()
        LOGGER.info(f"YtDLBot was started on @{bot.username}.")

    async def stop(self, *args):
        await super().stop()

        shutil.rmtree(Config.DOWNLOAD_DIR, ignore_errors=True)
        LOGGER.info("YtDLBot stopped. Bye.")
