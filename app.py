import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from converters import convert_video, convert_audio, convert_image, convert_document, convert_archive
import shutil

# Create necessary directories
Path("uploads").mkdir(exist_ok=True)
Path("converted").mkdir(exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return JSONResponse(content={"filename": file.filename}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/options/{filename}")
async def get_options(filename: str):
    try:
        file_extension = os.path.splitext(filename)[1][1:].lower()
        if file_extension in ["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "ogv", "gif", "mpeg", "m4v", "3gp", "vob"]:
            formats = ["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "gif"]
        elif file_extension in ["mp3", "wav", "flac"]:
            formats = ["mp3", "wav", "flac", "aac", "ogg"]
        elif file_extension in ["jpg", "png", "gif", "bmp"]:
            formats = ["jpg", "png", "gif", "bmp", "tiff", "webp"]
        elif file_extension in ["pdf", "docx", "txt"]:
            formats = ["pdf", "docx", "txt", "rtf"]
        elif file_extension in ["zip", "tar"]:
            formats = ["tar"] if file_extension == "zip" else ["zip"]
        else:
            formats = []
        return {"formats": formats}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid file format")

@app.post("/convert")
async def convert_file(filename: str, output_format: str):
    try:
        file_extension = os.path.splitext(filename)[1][1:].lower()
        input_path = f"uploads/{filename}"
        output_filename = f"{os.path.splitext(filename)[0]}.{output_format}"
        output_path = f"converted/{output_filename}"

        if file_extension in ["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "ogv", "gif", "mpeg", "m4v", "3gp", "vob"]:
            convert_video(input_path, "converted", output_format)
        elif file_extension in ["mp3", "wav", "flac"]:
            convert_audio(input_path, "converted", output_format)
        elif file_extension in ["jpg", "png", "gif", "bmp"]:
            convert_image(input_path, "converted", output_format)
        elif file_extension in ["pdf", "docx", "txt"]:
            convert_document(input_path, "converted", output_format)
        elif file_extension in ["zip", "tar"]:
            convert_archive(input_path, "converted", output_format)
        else:
            raise ValueError("Unsupported file type")

        return {"converted_filename": output_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"converted/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)