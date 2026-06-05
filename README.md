  
# MarkItDown Studio 🚀

MarkItDown Studio is a powerful, production-ready, multi-modal ingestion web application built with Streamlit. It seamlessly processes structured data, unstructured documents, heavy media files, and images, transforming them into clean, standardized Markdown format. 

Designed for LLM context compatibility, the application features an integrated real-time analytics dashboard to track word counts, character lengths, and token counts against popular LLM window constraints.

---

## 🌟 Key Features

* **Universal Document Processing:** Converts files like `.xlsx`, `.csv`, `.docx`, `.pptx`, `.pdf`, `.json`, `.xml`, and `.md` into clean Markdown formats using Microsoft's MarkItDown engine.
* **Intelligent OCR Engine:** Extracts text from images (`.png`, `.jpg`, `.jpeg`, `.webp`) dynamically using a custom backend powered by EasyOCR.
* **AI-Powered Audio & Video Transcription:** Transcribes multi-format media files into text utilizing `faster-whisper` and parses structural metadata using `pymediainfo`.
* **Token & Analytics Dashboard:** Instantly calculates token limits using OpenAI's `cl100k_base` tokenizer (`tiktoken`) and checks compliance against context windows for GPT-4, Claude 3, and Gemini 1.5.
* **Zip Ingestion Engine:** Accepts compressed `.zip` directories, maps internal structures, and processes multi-modal contents sequentially.

---

## 🛠️ Tech Stack & Core Dependencies

* **Frontend UI:** Streamlit (v1.58+)
* **Core Engine:** Microsoft MarkItDown (`markitdown[all]`)
* **Transcription:** Faster-Whisper, MoviePy
* **Computer Vision (OCR):** EasyOCR, OpenCV-Python-Headless
* **Tokenization:** Tiktoken
* **Package Management:** `uv` (Fast dependency resolver)

---

## ⚙️ Cloud Deployment Configuration

Deploying heavy multi-modal neural network pipelines to cloud servers (such as Streamlit Community Cloud) requires strict underlying Linux environment configurations alongside traditional Python dependencies.

### 1. System Packages (`packages.txt`)
Create a `packages.txt` file at the root of your repository to ensure the underlying Debian server initializes all the mandatory multi-threading, dynamic linking, and image rendering libraries:

```text
ffmpeg
libgl1
mediainfo
libgomp1
libsm6
libxext6
Python Dependencies (requirements.txt)
Ensure your requirements.txt leverages the modular document extras required for processing proprietary enterprise formats:

Plaintext
streamlit>=1.58.0
markitdown[all]
faster-whisper
easyocr
moviepy
pymediainfo
tiktoken
pandas
opencv-python-headless
🚀 Local Installation & Setup
Follow these steps to run the studio environment locally:

Clone the Repository:

Bash
git clone [https://github.com/your-username/markitdown-studio.git](https://github.com/your-username/markitdown-studio.git)
cd markitdown-studio
Set Up a Virtual Environment:

Bash
python -bin -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
Install Dependencies:
Using uv for ultra-fast installations is recommended:

Bash
pip install uv
uv pip install -r requirements.txt
Launch the Application:

Bash
streamlit run app.py
📂 Project Architecture
Plaintext
markitdown-studio/
│
├── app.py                # Main Streamlit UI entry point and state manager
├── processors.py         # Routing core for OCR, Whisper transcription, and MarkItDown
├── utils.py              # Auxiliary token analytics, file system tasks, and metadata lookups
├── requirements.txt      # Core Python library dependencies
└── packages.txt          # Essential Debian binary libraries
💡 Architecture & Optimizations
Dynamic VRAM/RAM Management: The pipeline initializes heavy AI models (EasyOCR and Faster-Whisper) dynamically on-demand, executing systematic garbage collection (gc.collect()) when switching languages or models to operate flawlessly within strict cloud memory constraints.

Headless Visual Processing: Utilizes opencv-python-headless to eliminate GUI processing overhead, reducing server resource footprint.

Safe Subprocess Management: Employs temporary context management windows to cleanly process files, preventing cache build-ups and data leaks on shared server instances.
