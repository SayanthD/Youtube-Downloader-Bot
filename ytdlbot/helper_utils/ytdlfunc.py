from __future__ import unicode_literals

from pyrogram.types import InlineKeyboardButton

import youtube_dl
from ytdlbot import LOGGER
from ytdlbot.helper_utils.util import humanbytes


def create_buttons(quailitylist):
    def buttonmap(item):
        if item["format"]:
            media_type = "Audio" if "audio" in item["format"] else "Video"
            return [
                InlineKeyboardButton(
                    f"{item['format']} {humanbytes(item['filesize'])}",
                    callback_data=f"ytdata|{media_type}|{item['format_id']}|{item['yturl']}"
                )
            ]
    # Return a array of Buttons
    return map(buttonmap, quailitylist)


# extract Youtube info
def extractYt(yturl):
    ydl = youtube_dl.YoutubeDL()
    with ydl:
        qualityList = []
        r = ydl.extract_info(yturl, download=False)
        for format in r["formats"]:
            # Filter dash video(without audio)
            if "dash" not in str(format["format"]).lower():
                qualityList.append(
                    {
                        "format": format["format"],
                        "filesize": format["filesize"],
                        "format_id": format["format_id"],
                        "yturl": yturl,
                    }
                )

        return r["title"], r["thumbnail"], qualityList


# The codes below were referenced after
# https://github.com/eyaadh/megadlbot_oss/blob/master/mega/helpers/ytdl.py
async def yt_download(url, media_type, format_id, output):
    ytdl_opts = {}
    if media_type == "Audio":
        ytdl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{output}",
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": f"{format_id}"
            }, {
                    "key": "FFmpegMetadata"
                }],
        }
    elif media_type == "Video":
        ytdl_opts = {
            "format": f"{format_id}+bestaudio",
            "outtmpl": f"{output}",
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegMetadata"
            }],
        }
    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        ydl.download([url])
    return True
