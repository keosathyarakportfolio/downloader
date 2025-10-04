from fastapi import FastAPI , Form , BackgroundTasks
from fastapi.responses import FileResponse , HTMLResponse
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
@app.get("/hello") 
def hello():
    return {"message": "Hello, World!"}   
@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vercel + FastAPI</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                background-color: #000000;
                color: #ffffff;
                line-height: 1.6;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            header {
                border-bottom: 1px solid #333333;
                padding: 0;
            }
            
            nav {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                padding: 1rem 2rem;
                gap: 2rem;
            }
            
            .logo {
                font-size: 1.25rem;
                font-weight: 600;
                color: #ffffff;
                text-decoration: none;
            }
            
            .nav-links {
                display: flex;
                gap: 1.5rem;
                margin-left: auto;
            }
            
            .nav-links a {
                text-decoration: none;
                color: #888888;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-size: 0.875rem;
                font-weight: 500;
            }
            
            .nav-links a:hover {
                color: #ffffff;
                background-color: #111111;
            }
            
            main {
                flex: 1;
                max-width: 1200px;
                margin: 0 auto;
                padding: 4rem 2rem;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            
            .hero {
                margin-bottom: 3rem;
            }
            
            .hero-code {
                margin-top: 2rem;
                width: 100%;
                max-width: 900px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            }
            
            .hero-code pre {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 1.5rem;
                text-align: left;
                grid-column: 1 / -1;
            }
            
            h1 {
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 1rem;
                background: linear-gradient(to right, #ffffff, #888888);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                font-size: 1.25rem;
                color: #888888;
                margin-bottom: 2rem;
                max-width: 600px;
            }
            
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                width: 100%;
                max-width: 900px;
            }
            
            .card {
                background-color: #111111;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 1.5rem;
                transition: all 0.2s ease;
                text-align: left;
            }
            
            .card:hover {
                border-color: #555555;
                transform: translateY(-2px);
            }
            
            .card h3 {
                font-size: 1.125rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #ffffff;
            }
            
            .card p {
                color: #888888;
                font-size: 0.875rem;
                margin-bottom: 1rem;
            }
            
            .card a {
                display: inline-flex;
                align-items: center;
                color: #ffffff;
                text-decoration: none;
                font-size: 0.875rem;
                font-weight: 500;
                padding: 0.5rem 1rem;
                background-color: #222222;
                border-radius: 6px;
                border: 1px solid #333333;
                transition: all 0.2s ease;
            }
            
            .card a:hover {
                background-color: #333333;
                border-color: #555555;
            }
            
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background-color: #0070f3;
                color: #ffffff;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 500;
                margin-bottom: 2rem;
            }
            
            .status-dot {
                width: 6px;
                height: 6px;
                background-color: #00ff88;
                border-radius: 50%;
            }
            
            pre {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 1rem;
                overflow-x: auto;
                margin: 0;
            }
            
            code {
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                font-size: 0.85rem;
                line-height: 1.5;
                color: #ffffff;
            }
            
            /* Syntax highlighting */
            .keyword {
                color: #ff79c6;
            }
            
            .string {
                color: #f1fa8c;
            }
            
            .function {
                color: #50fa7b;
            }
            
            .class {
                color: #8be9fd;
            }
            
            .module {
                color: #8be9fd;
            }
            
            .variable {
                color: #f8f8f2;
            }
            
            .decorator {
                color: #ffb86c;
            }
            
            @media (max-width: 768px) {
                nav {
                    padding: 1rem;
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .nav-links {
                    margin-left: 0;
                }
                
                main {
                    padding: 2rem 1rem;
                }
                
                h1 {
                    font-size: 2rem;
                }
                
                .hero-code {
                    grid-template-columns: 1fr;
                }
                
                .cards {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/" class="logo">Vercel + FastAPI</a>
                <div class="nav-links">
                    <a href="/docs">API Docs</a>
                    <a href="/api/data">API</a>
                </div>
            </nav>
        </header>
        <main>
            <div class="hero">
                <h1>Vercel + FastAPI</h1>
                <div class="hero-code">
                    <pre><code><span class="keyword">from</span> <span class="module">fastapi</span> <span class="keyword">import</span> <span class="class">FastAPI</span>

<span class="variable">app</span> = <span class="class">FastAPI</span>()

<span class="decorator">@app.get</span>(<span class="string">"/"</span>)
<span class="keyword">def</span> <span class="function">read_root</span>():
    <span class="keyword">return</span> {<span class="string">"Python"</span>: <span class="string">"on Vercel"</span>}</code></pre>
                </div>
            </div>
            
            <div class="cards">
                <div class="card">
                    <h3>Interactive API Docs</h3>
                    <p>Explore this API's endpoints with the interactive Swagger UI. Test requests and view response schemas in real-time.</p>
                    <a href="/docs">Open Swagger UI →</a>
                </div>
                
                <div class="card">
                    <h3>Sample Data</h3>
                    <p>Access sample JSON data through our REST API. Perfect for testing and development purposes.</p>
                    <a href="/api/data">Get Data →</a>
                </div>
                
            </div>
        </main>
    </body>
    </html>
    """
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
