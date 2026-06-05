import os
import zipfile
import easyocr
import gc
from markitdown import MarkItDown
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip  # Corrected Import

# Global instances and trackers for memory management
_ocr_reader = None
_current_ocr_langs = []

_whisper_model = None
_current_whisper_size = ""

_md_engine = MarkItDown()

def get_ocr_reader(langs: list):
    """Loads EasyOCR dynamically and clears old models from RAM if language changes."""
    global _ocr_reader, _current_ocr_langs
    
    if _ocr_reader is None or set(_current_ocr_langs) != set(langs):
        _ocr_reader = None
        gc.collect() 
        _ocr_reader = easyocr.Reader(langs)
        _current_ocr_langs = langs
        
    return _ocr_reader

def get_whisper_model(model_size: str):
    """Loads Whisper dynamically and clears old models from RAM if size changes."""
    global _whisper_model, _current_whisper_size
    
    if _whisper_model is None or _current_whisper_size != model_size:
        _whisper_model = None
        gc.collect() 
        _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        _current_whisper_size = model_size
        
    return _whisper_model

def process_document(file_path: str) -> str:
    try:
        result = _md_engine.convert(file_path)
        return result.text_content
    except Exception as e:
        return f"**Error processing document:** {str(e)}"

def process_image_ocr(file_path: str, langs: list = ['en']) -> str:
    try:
        reader = get_ocr_reader(langs)
        results = reader.readtext(file_path, detail=0)
        return "\n".join(results) if results else "*No text found in image.*"
    except Exception as e:
        return f"**Error in OCR processing:** {str(e)}"

def process_audio(file_path: str, model_size: str = "base") -> str:
    try:
        model = get_whisper_model(model_size)
        segments, info = model.transcribe(file_path, beam_size=5)
        text = "\n".join([segment.text for segment in segments])
        return text if text else "*No speech detected.*"
    except Exception as e:
        return f"**Error in audio transcription:** {str(e)}"

def process_video(file_path: str, temp_dir: str, model_size: str = "base") -> str:
    video = None
    try:
        audio_path = os.path.join(temp_dir, "extracted_audio.mp3")
        video = VideoFileClip(file_path)
        
        if video.audio is None:
            video.close()
            return "*No audio track found in this video.*"
            
        video.audio.write_audiofile(audio_path, logger=None)
        
        # Explicitly release handles immediately to prevent Streamlit UI freezing
        video.audio.close()
        video.close()
        
        return process_audio(audio_path, model_size)
    except Exception as e:
        return f"**Error in video processing:** {str(e)}"
    finally:
        # Absolute safety net: guarantees file is unlocked even if an error occurs
        if video is not None:
            try:
                video.close()
            except:
                pass

def process_zip(file_path: str, temp_dir: str, ocr_langs: list, whisper_model: str) -> str:
    combined_markdown = []
    extract_path = os.path.join(temp_dir, "unzipped")
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            
        for root, _, files in os.walk(extract_path):
            for file in files:
                full_path = os.path.join(root, file)
                ext = file.lower().split('.')[-1]
                
                combined_markdown.append(f"\n\n---\n## File: {file}\n---\n")
                
                if ext in ['pdf', 'docx', 'pptx', 'xlsx', 'csv', 'html', 'json', 'xml', 'txt', 'md']:
                    combined_markdown.append(process_document(full_path))
                elif ext in ['png', 'jpg', 'jpeg', 'webp']:
                    combined_markdown.append(process_image_ocr(full_path, ocr_langs))
                elif ext in ['mp3', 'wav', 'm4a', 'flac']:
                    combined_markdown.append(process_audio(full_path, whisper_model))
                elif ext in ['mp4', 'mov', 'avi', 'mkv']:
                    combined_markdown.append(process_video(full_path, temp_dir, whisper_model))
                else:
                    combined_markdown.append(f"*Skipped unsupported file type: {ext}*")
                    
        return "".join(combined_markdown)
    except Exception as e:
        return f"**Error processing ZIP archive:** {str(e)}"
