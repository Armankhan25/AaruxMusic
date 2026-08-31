import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", None)

BOT_TOKEN = getenv("BOT_TOKEN", None)

MONGO_DB_URI = getenv("MONGO_DB_URI", None)

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 1700))

LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "0"))

OWNER_ID = int(getenv("OWNER_ID", "0"))

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

API_URL = getenv("API_URL", "yt-api-production-2e61.up.railway.app") #youtube song url
API_KEY = getenv("API_KEY", None) # Get This API KEY FROM OWNER: @SpYtAPIBot

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Armankhan25/AaruxMusic",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/max_dev_server") 
SUPPORT_GROUP = getenv("SUPPORT_GROUP", "https://t.me/max_dev_server")

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))

PRIVACY_LINK = getenv("PRIVACY_LINK", "https://telegra.ph/Privacy-Policy-for-AaruxMusic-08-14")


SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)


PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))


TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 2145386496))


STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


START_IMG_URL = getenv(
    "START_IMG_URL", "https://carder.top/imagens/1788142044405-170282420.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://carder.top/imagens/1788142044405-170282420.jpg"
)
PLAYLIST_IMG_URL = "https://carder.top/imagens/1788142400893-380628487.jpg"
STATS_IMG_URL = "https://carder.top/imagens/1788142576518-34825811.jpg"
TELEGRAM_AUDIO_URL = "https://carder.top/imagens/1788142853056-270417129.jpg"
TELEGRAM_VIDEO_URL = "https://carder.top/imagens/1788142853056-270417129.jpg"
STREAM_IMG_URL = "https://carder.top/imagens/1788142853056-270417129.jpg"
SOUNCLOUD_IMG_URL = "https://carder.top/imagens/1788144714701-720038602.jpg"
YOUTUBE_IMG_URL = "https://carder.top/imagens/1788142853056-270417129.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://carder.top/imagens/1788144714701-720038602.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://carder.top/imagens/1788144714701-720038602.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://carder.top/imagens/1788144714701-720038602.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_GROUP:
    if not re.match("(?:http|https)://", SUPPORT_GROUP):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_GROUP url is wrong. Please ensure that it starts with https://"
        )














