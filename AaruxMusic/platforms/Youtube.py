import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist

import config



API_URL = os.environ.get(
    "API_URL",
    getattr(
        config,
        "API_URL",
        "http://yt-api-production-de72.up.railway.app",
    ),
)

API_URL = (API_URL or "").strip().rstrip("/")

API_KEY = os.environ.get(
    "API_KEY",
    getattr(config, "API_KEY", None),
)

if API_KEY:
    API_KEY = API_KEY.strip()


DOWNLOAD_DIR = "downloads"



def time_to_seconds(time):
    try:
        stringt = str(time)
        return sum(
            int(x) * 60 ** i
            for i, x in enumerate(
                reversed(stringt.split(":"))
            )
        )
    except Exception:
        return 0


def extract_video_id(link: str):
    """
    Extract YouTube video ID from:
      https://youtube.com/watch?v=xxxx
      https://www.youtube.com/watch?v=xxxx&list=xxxx
      https://youtu.be/xxxx
      xxxx
    """

    if not link:
        return None

    link = str(link).strip()

    match = re.search(
        r"(?:youtu\.be/)([A-Za-z0-9_-]{6,})",
        link,
    )

    if match:
        return match.group(1)

    match = re.search(
        r"(?:youtube\.com/watch\?v=)([A-Za-z0-9_-]{6,})",
        link,
    )

    if match:
        return match.group(1)

    match = re.search(
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{6,})",
        link,
    )

    if match:
        return match.group(1)

    match = re.search(
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{6,})",
        link,
    )

    if match:
        return match.group(1)

    if re.fullmatch(
        r"[A-Za-z0-9_-]{6,}",
        link,
    ):
        return link

    return None


def youtube_url(video_id: str):
    return f"https://www.youtube.com/watch?v={video_id}"



async def api_download(
    link: str,
    download_type: str,
    timeout_seconds: int = 300,
):
    """
    Download media from your own YT API.

    API endpoint:
        GET /download

    Parameters:
        url
        type
        api_key

    Your API returns the actual media file as binary data.
    """

    if not API_URL:
        print("[YT API] ERROR: API_URL is empty")
        return None

    if not API_KEY:
        print("[YT API] ERROR: API_KEY is empty")
        return None

    video_id = extract_video_id(link)

    if not video_id:
        print(f"[YT API] ERROR: Invalid YouTube URL/ID: {link}")
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    extension = "mp3" if download_type == "audio" else "mp4"

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.{extension}",
    )

    if (
        os.path.exists(file_path)
        and os.path.getsize(file_path) > 0
    ):
        print(
            f"[YT API] Using cached file: {file_path}"
        )
        return file_path

    endpoint = f"{API_URL}/download"

    params = {
        "url": video_id,
        "type": download_type,
        "api_key": API_KEY,
    }

    print(
        f"[YT API] Requesting {download_type}: "
        f"{video_id}"
    )

    try:

        timeout = aiohttp.ClientTimeout(
            total=timeout_seconds,
            connect=30,
            sock_read=timeout_seconds,
        )

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                endpoint,
                params=params,
                allow_redirects=True,
            ) as response:

                print(
                    f"[YT API] HTTP STATUS: "
                    f"{response.status}"
                )


                if response.status == 200:

                    content_type = (
                        response.headers.get(
                            "Content-Type",
                            "",
                        )
                        .lower()
                    )

                    print(
                        f"[YT API] Content-Type: "
                        f"{content_type}"
                    )

                    if (
                        "application/json"
                        in content_type
                    ):
                        try:
                            error_data = (
                                await response.json(
                                    content_type=None
                                )
                            )

                            print(
                                "[YT API] ERROR RESPONSE:",
                                error_data,
                            )

                        except Exception:
                            text = await response.text()
                            print(
                                "[YT API] ERROR RESPONSE:",
                                text[:1000],
                            )

                        return None

                    temp_path = (
                        f"{file_path}.part"
                    )

                    try:

                        with open(
                            temp_path,
                            "wb",
                        ) as file:

                            async for chunk in response.content.iter_chunked(
                                1024 * 128
                            ):

                                if chunk:
                                    file.write(chunk)

                        if (
                            not os.path.exists(
                                temp_path
                            )
                            or os.path.getsize(
                                temp_path
                            )
                            <= 0
                        ):
                            print(
                                "[YT API] "
                                "Downloaded file is empty"
                            )

                            return None

                        os.replace(
                            temp_path,
                            file_path,
                        )

                        print(
                            "[YT API] Download "
                            "successful:",
                            file_path,
                            "size=",
                            os.path.getsize(
                                file_path
                            ),
                        )

                        return file_path

                    except Exception as e:

                        print(
                            "[YT API] File write "
                            "error:",
                            repr(e),
                        )

                        try:
                            if os.path.exists(
                                temp_path
                            ):
                                os.remove(
                                    temp_path
                                )
                        except Exception:
                            pass

                        return None


                try:
                    error_data = await response.json(
                        content_type=None
                    )
                except Exception:

                    try:
                        error_data = (
                            await response.text()
                        )
                    except Exception:
                        error_data = ""

                print(
                    "[YT API] ERROR:",
                    error_data,
                )

                if response.status == 401:
                    print(
                        "[YT API] Authentication "
                        "failed. Check API_KEY."
                    )

                elif response.status == 403:
                    print(
                        "[YT API] Subscription "
                        "expired/inactive."
                    )

                elif response.status == 429:
                    print(
                        "[YT API] Request limit "
                        "exceeded."
                    )

                elif response.status == 400:
                    print(
                        "[YT API] Invalid "
                        "parameters."
                    )

                elif response.status >= 500:
                    print(
                        "[YT API] Server-side "
                        "download error."
                    )

                return None

    except asyncio.TimeoutError:

        print(
            "[YT API] ERROR: Request timeout"
        )

        return None

    except aiohttp.ClientError as e:

        print(
            "[YT API] HTTP CLIENT ERROR:",
            repr(e),
        )

        return None

    except Exception as e:

        print(
            "[YT API] UNEXPECTED ERROR:",
            repr(e),
        )

        return None



async def download_song(link: str) -> str:

    return await api_download(
        link,
        "audio",
        timeout_seconds=300,
    )



async def download_video(link: str) -> str:

    return await api_download(
        link,
        "video",
        timeout_seconds=600,
    )



class YouTubeAPI:

    def __init__(self):

        self.base = (
            "https://www.youtube.com/watch?v="
        )

        self.regex = (
            r"(?:youtube\.com|youtu\.be)"
        )

        self.status = (
            "https://www.youtube.com/oembed?url="
        )

        self.listbase = (
            "https://youtube.com/playlist?list="
        )

        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )


    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        return bool(
            re.search(
                self.regex,
                link,
            )
        )


    async def url(
        self,
        message_1: Message,
    ) -> Union[str, None]:

        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(
                message_1.reply_to_message
            )

        for message in messages:

            if message.entities:

                for entity in message.entities:

                    if (
                        entity.type
                        == MessageEntityType.URL
                    ):

                        text = (
                            message.text
                            or message.caption
                        )

                        if text:
                            return text[
                                entity.offset:
                                entity.offset
                                + entity.length
                            ]

            elif message.caption_entities:

                for entity in (
                    message.caption_entities
                ):

                    if (
                        entity.type
                        == MessageEntityType.TEXT_LINK
                    ):
                        return entity.url

        return None


    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            results = VideosSearch(
                link,
                limit=1,
            )

            res = await results.next()

        except Exception as e:

            print(
                "[YouTube] details error:",
                repr(e),
            )

            return "", "0:00", 0, "", ""

        if (
            not res
            or not res.get("result")
        ):
            return "", "0:00", 0, "", ""

        for result in res["result"]:

            title = result.get(
                "title",
                "",
            )

            duration_min = result.get(
                "duration",
                "0:00",
            )

            thumbnails = result.get(
                "thumbnails",
                [],
            )

            thumbnail = (
                thumbnails[0]["url"].split("?")[0]
                if thumbnails
                else ""
            )

            vidid = result.get(
                "id",
                "",
            )

            duration_sec = (
                int(
                    time_to_seconds(
                        duration_min
                    )
                )
                if duration_min
                else 0
            )

            return (
                title,
                duration_min,
                duration_sec,
                thumbnail,
                vidid,
            )

        return "", "0:00", 0, "", ""


    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            results = VideosSearch(
                link,
                limit=1,
            )

            res = await results.next()

        except Exception:
            return ""

        if (
            res
            and res.get("result")
        ):

            for result in res["result"]:

                return result.get(
                    "title",
                    "",
                )

        return ""


    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            results = VideosSearch(
                link,
                limit=1,
            )

            res = await results.next()

        except Exception:
            return "0:00"

        if (
            res
            and res.get("result")
        ):

            for result in res["result"]:

                return result.get(
                    "duration",
                    "0:00",
                )

        return "0:00"


    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            results = VideosSearch(
                link,
                limit=1,
            )

            res = await results.next()

        except Exception:
            return ""

        if (
            res
            and res.get("result")
        ):

            for result in res["result"]:

                thumbnails = result.get(
                    "thumbnails",
                    [],
                )

                return (
                    thumbnails[0]["url"].split("?")[0]
                    if thumbnails
                    else ""
                )

        return ""


    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            downloaded_file = (
                await download_video(link)
            )

            if downloaded_file:
                return 1, downloaded_file

            return 0, "Video download failed"

        except Exception as e:

            print(
                "[YouTube] video error:",
                repr(e),
            )

            return 0, (
                f"Video download error: {e}"
            )


    async def playlist(
        self,
        link,
        limit,
        user_id,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.listbase + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            plist = await Playlist.get(
                link
            )

        except Exception as e:

            print(
                "[YouTube] playlist error:",
                repr(e),
            )

            return []

        videos = (
            plist.get("videos")
            or []
        )

        ids = []

        for data in videos[:limit]:

            if not data:
                continue

            vid = data.get("id")

            if not vid:
                continue

            ids.append(vid)

        return ids


    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            results = VideosSearch(
                link,
                limit=1,
            )

            res = await results.next()

        except Exception as e:

            print(
                "[YouTube] track error:",
                repr(e),
            )

            return {}, ""

        if (
            not res
            or not res.get("result")
        ):
            return {}, ""

        for result in res["result"]:

            title = result.get(
                "title",
                "",
            )

            duration_min = result.get(
                "duration",
                "0:00",
            )

            vidid = result.get(
                "id",
                "",
            )

            yturl = result.get(
                "link",
                "",
            )

            thumbnails = result.get(
                "thumbnails",
                [],
            )

            thumbnail = (
                thumbnails[0]["url"].split("?")[0]
                if thumbnails
                else ""
            )

            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }

            return track_details, vidid

        return {}, ""


    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        ytdl_opts = {
            "quiet": True,
        }

        ydl = yt_dlp.YoutubeDL(
            ytdl_opts
        )

        with ydl:

            formats_available = []

            try:

                r = ydl.extract_info(
                    link,
                    download=False,
                )

            except Exception as e:

                print(
                    "[YouTube] formats error:",
                    repr(e),
                )

                return [], link

            for format_data in r.get(
                "formats",
                [],
            ):

                try:

                    if (
                        "dash"
                        not in str(
                            format_data[
                                "format"
                            ]
                        ).lower()
                    ):

                        formats_available.append(
                            {
                                "format": format_data[
                                    "format"
                                ],
                                "filesize": format_data.get(
                                    "filesize"
                                ),
                                "format_id": format_data[
                                    "format_id"
                                ],
                                "ext": format_data[
                                    "ext"
                                ],
                                "format_note": format_data[
                                    "format_note"
                                ],
                                "yturl": link,
                            }
                        )

                except Exception:
                    continue

        return formats_available, link


    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            search = VideosSearch(
                link,
                limit=10,
            )

            res = await search.next()

        except Exception as e:

            print(
                "[YouTube] slider error:",
                repr(e),
            )

            return "", "0:00", "", ""

        result = (
            res.get("result")
            if res
            else []
        )

        if (
            not result
            or query_type >= len(result)
        ):
            return "", "0:00", "", ""

        selected = result[
            query_type
        ]

        title = selected.get(
            "title",
            "",
        )

        duration_min = selected.get(
            "duration",
            "0:00",
        )

        vidid = selected.get(
            "id",
            "",
        )

        thumbnails = selected.get(
            "thumbnails",
            [],
        )

        thumbnail = (
            thumbnails[0]["url"].split("?")[0]
            if thumbnails
            else ""
        )

        return (
            title,
            duration_min,
            thumbnail,
            vidid,
        )


    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        try:

            if video:

                downloaded_file = (
                    await download_video(
                        link
                    )
                )

            else:

                downloaded_file = (
                    await download_song(
                        link
                    )
                )

            if downloaded_file:

                return (
                    downloaded_file,
                    True,
                )

            return None, False

        except Exception as e:

            print(
                "[YouTube] download error:",
                repr(e),
            )

            return None, False



YouTube = YouTubeAPI()
