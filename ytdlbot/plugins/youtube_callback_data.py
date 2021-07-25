import asyncio
import logging
import os
import shutil

from pyrogram import Client, ContinuePropagation
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaVideo,
)

from ytdlbot import Config
from ytdlbot.helper_utils.util import media_duration, width_and_height
from ytdlbot.helper_utils.ytdlfunc import yt_download

logger = logging.getLogger(__name__)


@Client.on_callback_query()
async def catch_youtube_fmtid(_, m):
    cb_data = m.data
    if cb_data.startswith("ytdata"):
        _, media_type, format_id, av_codec, video_id = cb_data.split("|")
        logger.info(cb_data)
        if media_type:
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{media_type}",
                            callback_data=f"{media_type}|{media_type}|{format_id}|{av_codec}|{video_id}",
                        ),
                        InlineKeyboardButton(
                            "Document",
                            callback_data=f"{media_type}|Document|{format_id}|{av_codec}|{video_id}",
                        ),
                    ]
                ]
            )
        await m.edit_message_reply_markup(buttons)

    else:
        raise ContinuePropagation


@Client.on_callback_query()
async def catch_youtube_dldata(c, q):
    cb_data = q.data
    # caption = q.message.caption
    user_id = q.from_user.id
    # Callback Data Assigning
    media_type, send_as, format_id, av_codec, video_id = cb_data.split("|")
    logger.info(cb_data)

    filext = "%(title)s.%(ext)s"
    userdir = os.path.join(os.getcwd(), Config.DOWNLOAD_DIR, str(user_id), video_id)

    if not os.path.isdir(userdir):
        os.makedirs(userdir)
    await q.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("Downloading...", callback_data="down")]]
        )
    )
    filepath = os.path.join(userdir, filext)
    # await q.edit_message_reply_markup([[InlineKeyboardButton("Processing..")]])

    fetch_media, caption = await yt_download(
        video_id, media_type, av_codec, format_id, filepath
    )
    if not fetch_media:
        await q.message.reply_text(caption)
        shutil.rmtree(userdir, ignore_errors=True)
        await q.message.delete()
        return
    else:
        logger.info(os.listdir(userdir))
        for content in os.listdir(userdir):
            if ".jpg" not in content:
                file_name = os.path.join(userdir, content)

    thumb = os.path.join(userdir, video_id + ".jpg")
    width = height = 0
    if os.path.isfile(thumb):
        width, height = width_and_height(thumb)
    else:
        thumb = None

    duration = media_duration(file_name)
    if send_as == "Audio":
        med = InputMediaAudio(
            media=file_name,
            thumb=thumb,
            duration=duration,
            caption=caption,
            title=caption,
        )

    elif send_as == "Video":
        med = InputMediaVideo(
            media=file_name,
            thumb=thumb,
            width=width,
            height=height,
            duration=duration,
            caption=caption,
            supports_streaming=True,
        )

    else:
        med = InputMediaDocument(
            media=file_name,
            thumb=thumb,
            caption=caption,
        )

    if med:
        loop = asyncio.get_event_loop()
        loop.create_task(send_file(c, q, med, userdir))
    else:
        logger.info("Media not found")


async def send_file(c, q, med, userdir):
    logger.info(med)
    try:
        await c.send_chat_action(chat_id=q.message.chat.id, action="upload_document")
        # this one is not working
        await q.edit_message_media(media=med)
    except Exception as e:
        logger.info(e)
        await q.edit_message_text(e)
    finally:
        shutil.rmtree(userdir, ignore_errors=True)  # Cleanup
