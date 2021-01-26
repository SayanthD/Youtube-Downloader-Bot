from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup

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
        title, thumbnail_url, buttons = await extract_formats(url)

        now = datetime.now()
        user_time[message.chat.id] = now + timedelta(minutes=Config.TIMEOUT)

    except Exception:
        await message.reply_text("`Failed To Fetch Youtube Data... 😔 \nPossible Youtube Blocked server ip \n#error`")
        return
    status = await message.reply_text("Fetching thumbnail...")
    thumbnail = await fetch_thumb(thumbnail_url, status.reply_to_message.message_id)
    try:
        # Todo add webp image support in thumbnail by default not supported by pyrogram
        # https://www.youtube.com/watch?v=lTTajzrSkCw
        await message.reply_photo(thumbnail, caption=title, reply_markup=InlineKeyboardMarkup(buttons))
        await status.delete()
    except Exception:
        try:
            thumbnail_url = "https://telegra.ph/file/ce37f8203e1903feed544.png"
            await message.reply_photo(thumbnail_url, caption=title, reply_markup=InlineKeyboardMarkup(buttons))
            await status.delete()
        except Exception as e:
            await status.edit(f"<code>{e}</code> #Error")
