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
from ytdlbot.helper_utils.ffmfunc import duration
from ytdlbot.helper_utils.ytdlfunc import shell_exec


@Client.on_callback_query()
async def catch_youtube_fmtid(_, m):
    cb_data = m.data
    if cb_data.startswith("ytdata"):
        _, media_type, format_id, yturl = cb_data.split("|")
        LOGGER.info(media_type)
        if media_type:
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"{media_type}", callback_data=f"{media_type}|{format_id}|{yturl}"
                        ),
                        InlineKeyboardButton(
                            "Document", callback_data=f"Document|{format_id}|{yturl}"
                        ),
                    ]
                ]
            )
        await m.edit_message_reply_markup(buttons)

    else:
        raise ContinuePropagation


@Client.on_callback_query()
async def catch_youtube_dldata(c, q):
    cb_data = q.data.strip()
    # Callback Data Check
    _, format_id, yturl = cb_data.split("|")
    if not cb_data.startswith(("Video", "Audio", "Document")):
        LOGGER.info("no data found")
        raise ContinuePropagation

    filext = "%(title)s.%(ext)s"
    userdir = os.path.join(os.getcwd(), Config.DOWNLOAD_DIR, str(q.message.reply_to_message.message_id))

    if not os.path.isdir(userdir):
        os.makedirs(userdir)
    await q.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("Downloading...", callback_data="down")]]
        )
    )
    filepath = os.path.join(userdir, filext)
    # await q.edit_message_reply_markup([[InlineKeyboardButton("Processing..")]])

    # The below and few other logics are copied from AnyDLBot/PublicLeech
    if cb_data.startswith("Audio"):
        cmd_to_exec = ["youtube-dl", "-c",
                       "--prefer-ffmpeg",
                       "--extract-audio",
                       "--audio-format", "mp3",
                       "--audio-quality", format_id,
                       "-o", filepath,
                       yturl,
                       ]
    else:
        cmd_to_exec = ["youtube-dl", "-c", "--embed-subs",
                       "-f", f"{format_id}+bestaudio",
                       "-o", filepath,
                       "--hls-prefer-ffmpeg",
                       yturl,
                       ]
    output, error = await shell_exec(cmd_to_exec)

    file_directory = os.listdir(os.path.dirname(filepath))
    for content in file_directory:
        file_name = os.path.join(userdir, content)

    loop = asyncio.get_event_loop()

    med = None
    if cb_data.startswith("Audio"):
        dur = round(duration(file_name))
        med = InputMediaAudio(
            media=file_name,
            duration=dur,
            caption=os.path.basename(file_name),
            title=os.path.basename(file_name),
        )

    elif cb_data.startswith("Video"):
        dur = round(duration(file_name))
        med = InputMediaVideo(
            media=file_name,
            duration=dur,
            caption=os.path.basename(file_name),
            supports_streaming=True,
        )

    else:
        med = InputMediaDocument(
            media=file_name,
            caption=os.path.basename(file_name),
        )

    if med:
        loop.create_task(send_file(c, q, med, userdir))
    else:
        LOGGER.info("Media not found")


async def send_file(c, q, med, userdir):
    LOGGER.info(med)
    try:
        await q.edit_message_reply_markup(
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("Uploading...", callback_data="down")]]
            )
        )
        await c.send_chat_action(chat_id=q.message.chat.id, action="upload_document")
        # this one is not working
        await q.edit_message_media(media=med)
    except Exception as e:
        LOGGER.info(e)
        await q.edit_message_text(e)
    finally:
        shutil.rmtree(userdir, ignore_errors=True)  # Cleanup
