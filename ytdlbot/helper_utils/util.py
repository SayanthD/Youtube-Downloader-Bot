from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


def humanbytes(size):
    # https://stackoverflow.com/a/43690506
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"


def width_and_height(thumbnail_path):
    metadata = extractMetadata(createParser(thumbnail_path))
    return metadata.get("width"), metadata.get("height")


def media_duration(media_path):
    metadata = extractMetadata(createParser(media_path))
    return metadata.get("duration").seconds
