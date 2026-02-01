from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
import os, time
from yt_dlp import YoutubeDL
import imageio_ffmpeg

app = FastAPI()

# ===============================
# Render-safe paths
# ===============================

BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
COOKIE_FILE = os.path.join(BASE_DIR, "cookies.txt")
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
PROXY = os.getenv("YTDLP_PROXY")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ===============================
# Helpers
# ===============================

def parse_quality(q):
    if not q:
        return (0, 0)
    try:
        if "p" in q:
            parts = q.replace("p", " ").split()
            h = int(parts[0])
            fps = int(parts[1]) if len(parts) > 1 else 0
            return (h, fps)
    except:
        pass
    return (0, 0)

def size(s):
    if not s:
        return "Unknown"
    s = s / (1024 * 1024)
    return f"{s:.2f} MB" if s < 1024 else f"{s/1024:.2f} GB"

def delete_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except:
        pass

# ===============================
# Routes
# ===============================

@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}

@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h2>FastAPI yt-dlp on Render</h2><p>Open /docs</p>"

# ===============================
# Get video info
# ===============================

@app.get("/get-video")
async def get_video(url: str):
    ydl_opts = {
        "quiet": True,
        "dump_json": True,
        "skip_download": True,
        "cookiefile": COOKIE_FILE,
        "ffmpeg_location": FFMPEG_PATH,
    }

    if PROXY:
        ydl_opts["proxy"] = PROXY

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = []
    seen = {}

    for f in info.get("formats", []):
        if f.get("vcodec") == "none":
            continue

        h = f.get("height")
        fps = f.get("fps")
        q = f"{h}p{fps}" if fps and fps > 30 else f"{h}p"

        if seen.get(q):
            continue
        seen[q] = True

        formats.append({
            "format_id": f.get("format_id"),
            "quality": q,
            "ext": f.get("ext"),
            "filesize": size(f.get("filesize")),
        })

    formats.sort(key=lambda x: parse_quality(x["quality"]), reverse=True)

    return {
        "title": info.get("title"),
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "formats": formats,
    }

# ===============================
# Download
# ===============================

@app.post("/download")
async def download(
    url: str = Form(...),
    format_id: str = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    name = str(int(time.time() * 1000))

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, f"{name}.%(ext)s"),
        "cookiefile": COOKIE_FILE,
        "ffmpeg_location": FFMPEG_PATH,
        "quiet": True,
    }

    if PROXY:
        ydl_opts["proxy"] = PROXY

    if format_id:
        ydl_opts["format"] = format_id
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }]
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    ext = info.get("ext", "mp4")
    path = os.path.join(DOWNLOAD_DIR, f"{name}.{ext}")
    filename = f"{info.get('title')}.{ext}"

    background_tasks.add_task(delete_file, path)

    return FileResponse(path, filename=filename, media_type="video/mp4")
