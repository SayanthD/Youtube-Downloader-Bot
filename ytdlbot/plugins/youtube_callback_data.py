import asyncio
import os
import shutil

from pyrogram import Client, ContinuePropagation

from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaVideo,
    InputMediaAudio,
    InputMediaDocument,
)

from ytdlbot import LOGGER
from ytdlbot.config import Config
from ytdlbot.helper_utils.ffmfunc import get_duration
from ytdlbot.helper_utils.ytdlfunc import yt_download


@Client.on_callback_query()
async def catch_youtube_fmtid(_, m):
    cb_data = m.data
    if cb_data.startswith("ytdata"):
        _, media_type, format_id, av_codec, video_id = cb_data.split("|")
        LOGGER.info(cb_data)
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
    caption = q.message.caption
    user_id = q.from_user.id
    # Callback Data Assigning
    media_type, send_as, format_id, av_codec, video_id = cb_data.split("|")
    LOGGER.info(cb_data)

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

    fetch_media = await yt_download(video_id, media_type, av_codec, format_id, filepath)
    if fetch_media:
        for content in os.listdir(userdir):
            if ".jpg" not in content:
                file_name = os.path.join(userdir, content)

    LOGGER.info(file_name)

    thumb = os.path.join(userdir, video_id + ".jpg")
    if not os.path.isfile(thumb):
        thumb = None

    loop = asyncio.get_event_loop()

    duration = await get_duration(file_name)
    if send_as == "Audio":
        med = InputMediaAudio(
            media=file_name,
            thumb=thumb,
            duration=duration,
            caption=caption,
            title=os.path.basename(file_name),
        )

    elif send_as == "Video":
        med = InputMediaVideo(
            media=file_name,
            thumb=thumb,
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
        loop.create_task(send_file(c, q, med, video_id, userdir))
    else:
        LOGGER.info("Media not found")


async def send_file(c, q, med, id, userdir):
    LOGGER.info(med)
    try:
        await q.edit_message_reply_markup(
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("Uploading...", callback_data="down")]]
            )
        )
        await c.send_chat_action(chat_id=q.message.chat.id, action="upload_document")
        # this one is not working
        await q.edit_message_media(
            media=med,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Watch in YouTube",
                            url=f"https://www.youtube.com/watch?v={id}",
                        )
                    ]
                ]
            ),
        )
    except Exception as e:
        LOGGER.info(e)
        await q.edit_message_text(e)
    finally:
        shutil.rmtree(userdir, ignore_errors=True)  # Cleanup
