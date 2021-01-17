import logging

# https://github.com/SpEcHiDe/PyroGramBot/blob/master/pyrobot/__init__.py

# the logging things
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)

LOGGER = logging.getLogger(__name__)

users = {}
user_time = {}
