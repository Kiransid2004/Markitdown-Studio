import streamlit as st
import os
import re
import processors as proc
import utils

# --- Configuration & Theme ---
st.set_page_config(
    page_title="MarkItDown Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Hide Streamlit UI ---
hide_streamlit_style = """
    <style>
    /* Hides the Deploy button and Top Toolbar */
    [data-testid="stToolbar"] {visibility: hidden !important;}
    /* Hides the default Streamlit Header entirely */
    header {visibility: hidden !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize Session State Variables
if 'markdown_output' not in st.session_state:
    st.session_state.markdown_output = ""
if 'analytics_data' not in st.session_state:
    st.session_state.analytics_data = {}
if 'metadata' not in st.session_state:
    st.session_state.metadata = {}
if 'uploader_id' not in st.session_state:
    st.session_state.uploader_id = 0  # Used to prevent 'ghost file' UI glitches

# --- Categorized Extensions ---
DOC_EXTS = ["pdf", "docx", "pptx", "xlsx", "csv", "json", "xml", "html", "txt", "md"]
EBOOK_EXTS = ["epub"]
IMG_EXTS = ["png", "jpg", "jpeg", "webp"]
AUDIO_EXTS = ["mp3", "wav", "m4a", "flac"]
VIDEO_EXTS = ["mp4", "mov", "avi", "mkv"]
ARCHIVE_EXTS = ["zip"]

ALL_EXTS = DOC_EXTS + EBOOK_EXTS + IMG_EXTS + AUDIO_EXTS + VIDEO_EXTS + ARCHIVE_EXTS

# --- Sidebar ---
with st.sidebar:
    st.title("📄 MarkItDown Studio")
    st.markdown("AI-Powered Document Intelligence Platform.")
    st.divider()
    
    st.subheader("⚙️ AI Configuration")
    
    ocr_languages = st.multiselect(
        "Image OCR Languages", 
        options=["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"], 
        default=["en"],
        help="Select the languages present in your images."
    )
    if not ocr_languages:
        ocr_languages = ["en"]
        
    whisper_size = st.selectbox(
        "Audio/Video Transcript Model",
        options=["tiny", "base", "small", "medium", "large-v3"],
        index=1,
        help="Use 'tiny' for maximum speed. Use 'base' or 'small' for better accuracy."
    )
    
    st.divider()
    st.subheader("🧹 Post-Processing Filters")
    st.markdown("Optimize text streams before token evaluation.")
    
    filter_whitespace = st.checkbox(
        "Compact Whitespace", 
        value=True, 
        help="Compress multiple consecutive blank lines down to a clean layout to reduce token usage."
    )
    filter_pii = st.checkbox(
        "Mask PII Data", 
        value=False, 
        help="Automatically identify and obfuscate sensitive fields like phone numbers and email strings."
    )
    filter_headers = st.checkbox(
        "Normalize Headers", 
        value=False, 
        help="Cleans standard structure spacing surrounding Markdown hash headings (#)."
    )
    
    st.divider()
    st.subheader("Supported Formats")
    st.caption(f"**Documents:** {', '.join(DOC_EXTS)}")
    st.caption(f"**Ebooks:** {', '.join(EBOOK_EXTS)}")
    st.caption(f"**Images:** {', '.join(IMG_EXTS)}")
    st.caption(f"**Media:** {', '.join(AUDIO_EXTS + VIDEO_EXTS)}")
    st.caption(f"**Archives:** {', '.join(ARCHIVE_EXTS)}")
    
# --- Main App Logic ---
st.header("Upload & Process")

# Dynamic uploader key forces a refresh if a file lock glitch occurs
uploaded_file = st.file_uploader(
    "Drag and drop documents, media, or archives here", 
    type=ALL_EXTS,
    key=f"file_uploader_{st.session_state.uploader_id}"
)

# Put the buttons side-by-side using Streamlit columns
col1, col2 = st.columns([1.5, 10])
with col1:
    processing_triggered = st.button("Process File", type="primary")
with col2:
    if st.button("🗑️ Clear Uploads"):
        # Instantly reset the uploader widget if the user gets stuck
        st.session_state.uploader_id += 1
        st.session_state.markdown_output = ""
        st.session_state.metadata = {}
        st.session_state.analytics_data = {}
        st.rerun()

# --- Processing Pipeline ---
if processing_triggered:
    if not uploaded_file:
        st.warning("⚠️ Please upload a valid, supported file first.")
    else:
        with st.spinner("Processing... This may take a moment for large files."):
            try:
                with utils.TempManager() as temp_dir:
                    markdown_result = ""
                    metadata_result = {}
                    
                    safe_name = utils.sanitize_filename(uploaded_file.name)
                    file_path = os.path.join(temp_dir, safe_name)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    ext = safe_name.split('.')[-1].lower()
                    
                    if ext in DOC_EXTS or ext in EBOOK_EXTS:
                        markdown_result = proc.process_document(file_path)
                    
                    elif ext in IMG_EXTS:
                        metadata_result = utils.get_image_metadata(file_path)
                        markdown_result = proc.process_image_ocr(file_path, langs=ocr_languages)
                    
                    elif ext in AUDIO_EXTS:
                        metadata_result = utils.get_audio_metadata(file_path)
                        markdown_result = proc.process_audio(file_path, model_size=whisper_size)
                    
                    elif ext in VIDEO_EXTS:
                        metadata_result = utils.get_video_metadata(file_path)
                        markdown_result = proc.process_video(file_path, temp_dir, model_size=whisper_size)
                    
                    elif ext in ARCHIVE_EXTS:
                        markdown_result = proc.process_zip(file_path, temp_dir, ocr_langs=ocr_languages, whisper_model=whisper_size)
                    
                    # --- Execution of Selected Post-Processing Filters ---
                    if markdown_result:
                        if filter_whitespace:
                            # Collapse three or more consecutive linebreaks to a clean double break
                            markdown_result = re.sub(r'\n{3,}', '\n\n', markdown_result)
                            # Remove trailing whitespace spaces from the ends of lines
                            markdown_result = '\n'.join([line.rstrip() for line in markdown_result.splitlines()])
                        
                        if filter_pii:
                            # Standard Email Pattern Masking
                            markdown_result = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', markdown_result)
                            # Global phone format masking (matches 7-15 digit sequences split by dots/dashes/spaces)
                            markdown_result = re.sub(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]', markdown_result)
                        
                        if filter_headers:
                            # Ensure exactly one space follows any markdown hashtag heading token if clumped together
                            markdown_result = re.sub(r'^(#+)([^#\s])', r'\1 \2', markdown_result, flags=re.MULTILINE)
                    
                    # Update Session State on Success
                    st.session_state.markdown_output = markdown_result
                    st.session_state.metadata = metadata_result
                    st.session_state.analytics_data = utils.calculate_analytics(markdown_result)
                    st.success("Processing complete!")
                    
            except Exception as e:
                st.error(f"A fatal error occurred: {str(e)}")
                # If a major error happens, cycle the uploader ID so the broken file doesn't get stuck on screen
                st.session_state.uploader_id += 1
                st.rerun()

# --- Output & Analytics Section ---
if st.session_state.markdown_output:
    st.divider()
    
    st.subheader("📊 Analytics Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Word Count", f"{st.session_state.analytics_data.get('words', 0):,}")
    col2.metric("Character Count", f"{st.session_state.analytics_data.get('chars', 0):,}")
    col3.metric("Token Count (cl100k)", f"{st.session_state.analytics_data.get('tokens', 0):,}")
    
    with st.expander("LLM Context Window Compatibility"):
        checks = st.session_state.analytics_data.get('context_checks', {})
        for model, is_compatible in checks.items():
            icon = "✅" if is_compatible else "❌"
            st.write(f"{icon} {model}")

    if st.session_state.metadata:
        with st.expander("📄 Extracted Metadata"):
            st.json(st.session_state.metadata)

    st.subheader("Output")
    tab_preview, tab_raw = st.tabs(["Markdown Preview", "Raw Markdown"])
    
    with tab_preview:
        st.markdown(st.session_state.markdown_output, unsafe_allow_html=True)
        
    with tab_raw:
        st.text_area("Raw Text", st.session_state.markdown_output, height=400)
        
    st.download_button(
        label="📥 Download Markdown (.md)",
        data=st.session_state.markdown_output,
        file_name="markitdown_output.md",
        mime="text/markdown",
        type="primary"
    )
st.caption("### Credits")
st.caption("Document conversion powered by Microsoft's [MarkItDown](https://github.com/microsoft/markitdown) library.")