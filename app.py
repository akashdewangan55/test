from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL
import os

app = FastAPI()

# Configure download options
ydl_opts_video = {
    'format': 'best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'quiet': True,
}

ydl_opts_audio = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
    }],
    'quiet': True,
}

@app.get("/")
def root():
    return {"message": "YouTube Downloader API is running."}

@app.get("/download/")
def download_video(url: str = Query(...), type: str = Query("video")):
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    try:
        ydl_opts = ydl_opts_audio if type == "audio" else ydl_opts_video
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if type == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"

        return JSONResponse({
            "title": info.get("title"),
            "filename": os.path.basename(filename),
            "path": f"/download_file/{os.path.basename(filename)}"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

from fastapi.responses import FileResponse

@app.get("/download_file/{filename}")
def download_file(filename: str):
    file_path = os.path.join("downloads", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return JSONResponse(status_code=404, content={"error": "File not found"})