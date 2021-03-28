from __future__ import unicode_literals

from pyrogram.types import InlineKeyboardButton

import youtube_dl
from ytdlbot import LOGGER
from ytdlbot.config import Config
from ytdlbot.helper_utils.util import humanbytes


# extract Youtube info
def extract_formats(yturl):
    with youtube_dl.YoutubeDL() as ydl:
        buttons = []
        info = ydl.extract_info(yturl, download=False, ie_key="Youtube")
        for listed in info.get("formats"):
            media_type = "Audio" if "audio" in listed.get("format") else "Video"
            # SpEcHiDe/AnyDLBot/anydlbot/plugins/youtube_dl_echo.py#L112
            filesize = humanbytes(listed.get("filesize")) if listed.get("filesize") else "(best)"
            # Filter dash video(without audio)
            if "dash" not in str(listed.get("format")).lower():
                buttons.append([
                    InlineKeyboardButton(
                        f"{media_type} {listed['format_note']} [{listed['ext']}] {filesize}",
                        callback_data=f"ytdata|{media_type}|{listed['format_id']}|{info['id']}"
                    )
                ])

    return info.get("id"), info.get("title"), info.get("thumbnail"), buttons


# The codes below were referenced after
# https://github.com/eyaadh/megadlbot_oss/blob/master/mega/helpers/ytdl.py
# https://stackoverflow.com/questions/33836593
def yt_download(video_id, media_type, format_id, output):
    ytdl_opts = {
        "outtmpl": output,
        "ignoreerrors": True,
        "nooverwrites": True,
        "continuedl": True,
        "noplaylist": True,
        "max_filesize": Config.MAX_SIZE
    }
    if media_type == "Audio":
        ytdl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": format_id
            }, {
                "key": "FFmpegMetadata"
            }],
        })
    elif media_type == "Video":
        ytdl_opts.update({
            "format": f"{format_id}+bestaudio",
            "postprocessors": [{
                "key": "FFmpegMetadata"
            }],
        })
    with youtube_dl.YoutubeDL(ytdl_opts) as ytdl:
        ytdl.download([video_id])
    return True
