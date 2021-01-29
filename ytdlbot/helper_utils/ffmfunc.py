import os
import subprocess

from ytdlbot.config import Config


async def get_duration(vid_file_path):
    """
    Video's duration in seconds, return a float number
    @vid_file_path : The absolute (full) path of the video file, string.
    """
    if not isinstance(vid_file_path, str):
        raise Exception('Give ffprobe a full file path of the file')

    # https://trac.ffmpeg.org/wiki/FFprobeTips
    command = ["ffprobe",
               "-v", "error",
               "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1",
               vid_file_path
               ]

    output, _ = await run_popen(command)
    return round(float(output)) if output else 0


async def fetch_thumb(thumbnail_url, video_id):
    down_dir = os.path.join(os.getcwd(), Config.DOWNLOAD_DIR, video_id)
    if not os.path.exists(down_dir):
        os.makedirs(down_dir)
    thumb_path = os.path.join(down_dir, video_id + ".jpg")

    # https://unix.stackexchange.com/a/349116
    await run_popen(["ffmpeg", "-n", "-i", thumbnail_url, thumb_path])
    return thumb_path


async def run_popen(command):
    process = subprocess.Popen(
        args=command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    return stdout, stderr
