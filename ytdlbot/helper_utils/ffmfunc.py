import os
import subprocess
import json

from ytdlbot.config import Config


async def get_duration(vid_file_path):
    """
    Video's duration in seconds, return a float number
    @vid_file_path : The absolute (full) path of the video file, string.
    """
    if not isinstance(vid_file_path, str):
        raise Exception('Give ffprobe a full file path of the file')

    command = ["ffprobe",
               "-loglevel", "quiet",
               "-print_format", "json",
               "-show_format",
               "-show_streams",
               vid_file_path
               ]

    output, _ = await run_popen(command)
    json_output = json.loads(output)

    duration = 0
    format_info = json_output.get("format")
    if format_info and "duration" in format_info:
        duration = round(float(format_info["duration"]))
    return duration


async def fetch_thumb(thumbnail_url, message_id):
    down_dir = os.path.join(os.getcwd(), Config.DOWNLOAD_DIR, str(message_id))
    if not os.path.exists(down_dir):
        os.makedirs(down_dir)
    thumb_path = os.path.join(down_dir, "thumbnail.jpg")
    command = ["ffmpeg",
               "-y",
               "-i", thumbnail_url,
               "-vf", "scale=320:-1",
               thumb_path
               ]
    output, _ = await run_popen(command)
    return thumb_path


async def run_popen(command):
    process = subprocess.Popen(
        args=command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    return stdout, stderr
