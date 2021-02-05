from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup
import youtube_dl

from ytdlbot.config import Config
from ytdlbot import user_time
from ytdlbot.helper_utils.ytdlfunc import extract_formats
from ytdlbot.helper_utils.ffmfunc import fetch_thumb

ytregex = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"


@Client.on_message(filters.regex(ytregex))
async def ytdl(_, message):
    userLastDownloadTime = user_time.get(message.chat.id)
    if userLastDownloadTime and userLastDownloadTime > datetime.now():
        wait_time = round((userLastDownloadTime - datetime.now()).total_seconds() / 60, 2)
        await message.reply_text(f"`Wait {wait_time} Minutes before next Request`")
        return

    url = message.text.strip()
    await message.reply_chat_action("typing")
    try:
        video_id, title, thumbnail_url, buttons = await extract_formats(url)

        now = datetime.now()
        user_time[message.chat.id] = now + timedelta(minutes=Config.TIMEOUT)

    except youtube_dl.utils.DownloadError as error:
        await message.reply_text(f"<b>{error}</b>", quote=True)
        return

    status = await message.reply_text("Fetching thumbnail...", quote=True)
    if Config.CUSTOM_THUMB:
        await status.edit_text("Found Custom thumbnail, Gotta pull it now.")
        thumbnail_url = Config.CUSTOM_THUMB
    thumbnail = await fetch_thumb(thumbnail_url, video_id)
    try:
        await message.reply_photo(thumbnail, caption=title, reply_markup=InlineKeyboardMarkup(buttons))
        await status.delete()
    except Exception as e:
        await status.edit(f"<code>{e}</code> #Error")
