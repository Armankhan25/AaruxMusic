import asyncio
import sys

if sys.platform != "win32":
    try:
        import uvloop
        uvloop.install()
    except (ImportError, Exception):
        pass

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
else:
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

try:
    import pytgcalls
except ModuleNotFoundError:
    import io, site, sysconfig, urllib.request, zipfile
    try:
        site_pkgs = sysconfig.get_paths().get("purelib") or site.getsitepackages()[0]
        url = "https://files.pythonhosted.org/packages/a7/eb/8cbe698f121db5975d04ca03d5cf599547d6928da5e1c456860d5b780447/py_tgcalls-0.9.7-cp311-none-any.whl"
        data = urllib.request.urlopen(url, timeout=30).read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(site_pkgs)
        import pytgcalls
    except Exception:
        pass


import AaruxMusic.core.patch

from AaruxMusic.core.bot import DevSp
from AaruxMusic.core.dir import dirr
from AaruxMusic.core.git import git
from AaruxMusic.core.userbot import Userbot
from AaruxMusic.misc import dbb, heroku

from AaruxMusic.logging import LOGGER


dirr()
git()
dbb()
heroku()


app = DevSp()
userbot = Userbot()


from AaruxMusic.platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
