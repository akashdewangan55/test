from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
import os

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace "*" with your frontend domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "YouTube Downloader API is running."}

@app.post("/api/download")
async def download_video(request: Request):
    data = await request.json()
    url = data.get("url")

    if not url:
        return JSONResponse(status_code=400, content={"status": "error", "message": "URL is required"})

    try:
        # Setup yt-dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
        }

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            video_title = info.get("title", "Downloaded Video")
            download_url = f"/download_file/{os.path.basename(filename)}"

        return {
            "status": "success",
            "title": video_title,
            "downloadUrl": download_url
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

from fastapi.responses import FileResponse

@app.get("/download_file/{filename}")
def serve_file(filename: str):
    file_path = os.path.join("downloads", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return JSONResponse(status_code=404, content={"status": "error", "message": "File not found"})