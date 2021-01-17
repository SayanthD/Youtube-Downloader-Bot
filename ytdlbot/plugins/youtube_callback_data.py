import asyncio
import os

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
from ytdlbot.helper_utils.ytdlfunc import downloadvideocli, downloadaudiocli


@Client.on_callback_query()
async def catch_youtube_fmtid(c, m):
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
    if not cb_data.startswith(("Video", "Audio", "docaudio", "Document")):
        LOGGER.info("no data found")
        raise ContinuePropagation

    filext = "%(title)s.%(ext)s"
    userdir = os.path.join(os.getcwd(), Config.DOWNLOAD_DIR, str(q.message.chat.id))

    if not os.path.isdir(userdir):
        os.makedirs(userdir)
    await q.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [[InlineKeyboardButton("Downloading...", callback_data="down")]]
        )
    )
    filepath = os.path.join(userdir, filext)
    # await q.edit_message_reply_markup([[InlineKeyboardButton("Processing..")]])

    audio_command = ["youtube-dl", "-c", "--prefer-ffmpeg",
                     "--extract-audio",
                     "--audio-format", "mp3",
                     "--audio-quality", format_id,
                     "-o", filepath,
                     yturl,
                     ]

    video_command = ["youtube-dl", "-c", "--embed-subs",
                     "-f", f"{format_id}+bestaudio",
                     "-o", filepath,
                     "--hls-prefer-ffmpeg",
                     yturl,
                     ]


    loop = asyncio.get_event_loop()

    med = None
    if cb_data.startswith("Audio"):
        filename = await downloadaudiocli(audio_command)
        dur = round(duration(filename))
        med = InputMediaAudio(
            media=filename,
            duration=dur,
            caption=os.path.basename(filename),
            title=os.path.basename(filename),
        )

    if cb_data.startswith("Video"):
        filename = await downloadvideocli(video_command)
        dur = round(duration(filename))
        med = InputMediaVideo(
            media=filename,
            duration=dur,
            caption=os.path.basename(filename),
            supports_streaming=True,
        )

    if cb_data.startswith("docaudio"):
        filename = await downloadaudiocli(audio_command)
        med = InputMediaDocument(
            media=filename,
            caption=os.path.basename(filename),
        )

    if cb_data.startswith("Document"):
        filename = await downloadvideocli(video_command)
        med = InputMediaDocument(
            media=filename,
            caption=os.path.basename(filename),
        )
    if med:
        loop.create_task(send_file(c, q, med, filename))
    else:
        LOGGER.info("med not found")


async def send_file(c, q, med, filename):
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
        try:
            os.remove(filename)
        except:
            pass
