# 📄 MarkItDown Studio

**An AI-Powered Document Intelligence & Conversion Platform.**

MarkItDown Studio is a robust, local-first web application built with Streamlit. It acts as a unified ingestion engine, allowing users to drop almost any file type (Documents, Images, Audio, Video, and Archives) into a conversational interface, extract the raw data, and convert it into clean, LLM-ready Markdown.

## ✨ Features

* **Universal File Ingestion:** Supports over 20+ file formats including PDFs, Office Documents, Ebooks, Images, Audio, Video, and ZIP archives.
* **Intelligent Routing:** Automatically detects file types and routes them to the appropriate processing engine (OCR, Audio Transcription, or Document Parsing).
* **Advanced Post-Processing:** Built-in data sanitization including whitespace optimization, Markdown header normalization, and automated PII redaction (masking emails and phone numbers).
* **Analytics Dashboard:** Real-time metrics calculating Word Count, Character Count, and exact Token Counts (using `cl100k_base`), alongside an LLM Context Window compatibility matrix.
* **Conversational Interface:** A clean, ChatGPT-style chat feed for easy interaction and history tracking.

## 🛠️ Tech Stack

* **Frontend/Framework:** [Streamlit](https://streamlit.io/)
* **Document Conversion:** Microsoft's [MarkItDown](https://github.com/microsoft/markitdown)
* **Image OCR:** [EasyOCR](https://github.com/JaidedAI/EasyOCR)
* **Media Transcription:** [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
* **Audio Extraction:** MoviePy & FFMPEG
* **Analytics:** Tiktoken (OpenAI)

## 🚀 Local Installation

To run MarkItDown Studio on your own machine, you will need Python 3.9+ and `ffmpeg` installed on your system.

**1. Clone the repository**
```bash
git clone [https://github.com/YOUR_USERNAME/markitdown-studio.git](https://github.com/YOUR_USERNAME/markitdown-studio.git)
cd markitdown-studio