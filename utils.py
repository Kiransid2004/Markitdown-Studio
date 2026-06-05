import os
import re
import shutil
import tempfile
import tiktoken
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen import File as MutagenFile
from pymediainfo import MediaInfo

# --- Analytics ---
def calculate_analytics(text: str) -> dict:
    """Calculates words, characters, and tokens."""
    if not text:
        return {"words": 0, "chars": 0, "tokens": 0, "context_checks": {}}
        
    word_count = len(text.split())
    char_count = len(text)
    
    # Token counting using cl100k_base (OpenAI)
    encoding = tiktoken.get_encoding("cl100k_base")
    token_count = len(encoding.encode(text))
    
    context_checks = {
        "32k (e.g., GPT-4)": token_count < 32000,
        "128k (e.g., GPT-4o)": token_count < 128000,
        "200k (e.g., Claude 3)": token_count < 200000,
        "1M (e.g., Gemini 1.5)": token_count < 1000000,
    }
    
    return {
        "words": word_count,
        "chars": char_count,
        "tokens": token_count,
        "context_checks": context_checks
    }

# --- Metadata Extraction ---
def get_image_metadata(file_path: str) -> dict:
    try:
        image = Image.open(file_path)
        meta = {"Format": image.format, "Mode": image.mode, "Size": f"{image.width}x{image.height}"}
        exifdata = image.getexif()
        if exifdata:
            for tag_id in exifdata:
                tag = TAGS.get(tag_id, tag_id)
                data = exifdata.get(tag_id)
                if isinstance(data, bytes):
                    data = data.decode(errors="replace")
                meta[tag] = data
        return meta
    except Exception as e:
        return {"Error": f"Failed to extract metadata: {str(e)}"}

def get_audio_metadata(file_path: str) -> dict:
    try:
        audio = MutagenFile(file_path)
        if audio and audio.info:
            return {
                "Duration (s)": round(audio.info.length, 2),
                "Bitrate (bps)": getattr(audio.info, 'bitrate', 'Unknown'),
                "Sample Rate (Hz)": getattr(audio.info, 'sample_rate', 'Unknown')
            }
        return {"Status": "No metadata found"}
    except Exception as e:
        return {"Error": str(e)}

def get_video_metadata(file_path: str) -> dict:
    try:
        media_info = MediaInfo.parse(file_path)
        for track in media_info.tracks:
            if track.track_type == "Video":
                return {
                    "Codec": track.format,
                    "Resolution": f"{track.width}x{track.height}",
                    "Duration (ms)": track.duration,
                    "Frame Rate": track.frame_rate
                }
        return {"Status": "No video track found"}
    except Exception as e:
        return {"Error": str(e)}

# --- Security & File Ops ---
def sanitize_filename(filename: str) -> str:
    """Removes path traversal and invalid characters."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    return filename

class TempManager:
    """Context manager for handling temporary directories securely."""
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def __enter__(self):
        return self.temp_dir
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir, ignore_errors=True)