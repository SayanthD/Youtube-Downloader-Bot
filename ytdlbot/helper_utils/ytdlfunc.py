from __future__ import unicode_literals

from pyrogram.types import InlineKeyboardButton

import youtube_dl
from ytdlbot import LOGGER
from ytdlbot.helper_utils.util import humanbytes
import asyncio


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


#  Need to work on progress

# def downloadyt(url, fmid, custom_progress):
#     ydl_opts = {
#         'format': f"{fmid}+bestaudio",
#         "outtmpl": "test+.%(ext)s",
#         'noplaylist': True,
#         'progress_hooks': [custom_progress],
#     }
#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([url])


# https://github.com/SpEcHiDe/AnyDLBot


async def downloadvideocli(command_to_exec):
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info(e_response)
    filename = t_response.split("Merging formats into")[-1].split('"')[1]
    return filename


async def downloadaudiocli(command_to_exec):
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    LOGGER.info("Download error:", e_response)

    return (
        t_response.split("Destination")[-1].split("Deleting")[0].split(":")[-1].strip()
    )
