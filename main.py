from fastapi import FastAPI , Form , BackgroundTasks
from fastapi.responses import FileResponse 
import os, time
from yt_dlp import YoutubeDL

app = FastAPI()

COOKIE_FILE = os.path.join(os.getcwd(), "cookies.txt")  # ✅ path cookies

def parse_quality(q):
    if not q:
        return (0, 0)
    try:
        if "p" in q:
            parts = q.replace("p", " ").split()
            height = int(parts[0])
            fps = int(parts[1]) if len(parts) > 1 else 0
            return (height, fps)
    except:
        return (0, 0)
    return (0, 0)

def size(size):
    if size is None:
        return "Unknown"
    size = size / (1024 * 1024)
    if size < 1024.0:
        return f"{size:.2f} MB"
    else:
        size = size / 1024.0
        return f"{size:.2f} GB"

@app.get("/get-video")
async def get_video(url: str):
    get_video = {
        "quiet": True,
        "dump_json": True,
        "skip_download": True,
        "cookiefile": COOKIE_FILE,   # ✅ បន្ថែម cookies
    }
    with YoutubeDL(get_video) as ydl:
        info = ydl.extract_info(url, download=False)

    thumbnail = info.get("thumbnail", "")
    title = info.get("title", "")
    duration = info.get("duration", 0)
    formats = []
    quality_list = {}

    for f in info.get("formats", []):
        if f.get("vcodec") != "none":
            height = f.get("height")
            width = f.get("width")
            format_note = f.get("format_note")
            fps = f.get("fps")
            quality = None
            if format_note:
                quality = format_note
            elif height:
                quality = f"{height}p{fps}" if fps and fps > 30 else f"{height}p"
            elif width:
                quality = f"{width}w{fps}" if fps and fps > 30 else f"{width}w"
            if quality:
                if quality_list.get(quality) is not None:
                    continue
                quality_list[quality] = True

            formats.append({
                "format_id": f.get("format_id"),
                "url": f.get("url"),
                "ext": f.get("ext"),
                "filesize": size(f.get("filesize")),
                "quality": quality if quality else "Unknown",
                "fps": fps,
            })

    formats = sorted(formats, key=lambda x: parse_quality(x["quality"]), reverse=True)
    return {
        "thumbnail": thumbnail,
        "title": title,
        "videoURL": url,
        "duration": duration,
        "formats": formats,
    }

def delete_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted: {path}")
    except Exception as e:
        print(f"Error deleting {path}: {e}")

@app.post("/download")
async def download(
    url: str = Form(...), 
    format_id: str = Form(None), 
    background_tasks: BackgroundTasks = None
):
    timename = str.format("{:.0f}", time.time() * 1000)
    download_dir = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    ydl_opts = {
        "outtmpl": os.path.join(download_dir, f"{timename}.%(ext)s"),
        "cookiefile": COOKIE_FILE,  # ✅ បន្ថែម cookies នៅទីនេះផងដែរ
    }

    if not format_id:
        ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio/best"
    else:
        ydl_opts["format"] = format_id
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }]

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    ext = info.get("ext", "mp4")
    filename = f"{info.get('title')}.{ext}"
    filepath = os.path.join(download_dir, f"{timename}.{ext}")

    background_tasks.add_task(delete_file, filepath)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="video/mp4"
    )
