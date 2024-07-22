"""
Piper TTS functionality for audiobook creation.

Author: Kieran Currie Rones
Date: July 22nd, 2024

This module contains the generation route for TTS.
"""

import streamlit as st
import ebooklib
from ebooklib import epub
import os
import tempfile
import re
from bs4 import BeautifulSoup
from tts_handler import generate_output_file
from configuration import VOICES_FOLDER, OUTPUT_FOLDER

def parse_epub(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name

    book = epub.read_epub(tmp_file_path)
    sections = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Try to find a title or header for this section
            title = soup.find(['h1', 'h2', 'h3', 'title'])
            title_text = title.text.strip() if title else f"Section {len(sections) + 1}"
            
            # Get the main content
            main_content = soup.get_text().strip()
            
            sections.append((title_text, main_content))

    os.unlink(tmp_file_path)  # Delete the temporary file
    return sections

def parse_mobi(file):
    # Placeholder for mobi parsing logic
    st.warning("Mobi parsing is not yet implemented.")
    return []

def split_text(text, max_chars):
    sentences = re.split('(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def sanitize_filename(filename):
    return ''.join(c for c in filename if c.isalnum() or c in (' ', '_')).strip()

def main():
    st.title("Audiobook Creator")
    uploaded_file = st.file_uploader("Choose an epub file", type=["epub"])
    if uploaded_file is not None:
        book_name = os.path.splitext(uploaded_file.name)[0]
        sections = parse_epub(uploaded_file)
        st.subheader("Select sections to include")
        selected_sections = []
        for i, (title, content) in enumerate(sections):
            if st.checkbox(f"{title}", key=f"section_{i}"):
                content = st.text_area(f"Content Preview ({title})", content, height=200, key=f"content_{i}")
                selected_sections.append((title, content))

        valid_voices = sorted([f for f in os.listdir(VOICES_FOLDER) if f.endswith('.onnx')])
        selected_voice = st.selectbox("Select Voice:", valid_voices)

        # Custom naming toggle and input
        use_custom_naming = st.toggle("Use custom naming for output folder/files")
        custom_name = ""
        if use_custom_naming:
            custom_name = st.text_input("Enter custom name for output folder/files:")
            if custom_name and not custom_name.isspace():
                book_name = sanitize_filename(custom_name)
            else:
                st.warning("Custom name is empty or invalid. Using default naming.")

        if st.button("Generate Audiobook"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i, (title, content) in enumerate(selected_sections):
                chunks = split_text(content, max_chars=4000000)
                for j, chunk in enumerate(chunks):
                    output_file = generate_output_file(chunk, selected_voice, book_name, i, j)
                    if output_file is None:
                        st.error(f"Failed to generate audio for {title}, chunk {j+1}")
                    else:
                        st.success(f"Generated: {output_file}")
                progress = (i + 1) / len(selected_sections)
                progress_bar.progress(progress)
                status_text.text(f"Processing: {title}")
            st.success("Audiobook generation completed!")

if __name__ == "__main__":
    main()
