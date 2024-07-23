"""
Piper TTS functionality for audiobook creation.

Author: Kieran Currie Rones
Date: July 23rd, 2024

This module contains all necessary functionality.
"""

import streamlit as st
import ebooklib
from ebooklib import epub
import os
import tempfile
import re
from bs4 import BeautifulSoup
import shutil
import logging
import subprocess
import shlex

# Configuration settings
VOICES_FOLDER = "./static/voices/"
OUTPUT_FOLDER = "./static/output/"
PIPER_LOCATION = "./piper/piper"

# Set up logging
logging.basicConfig(level=logging.INFO)

def split_into_sections(text, words_per_section=10000):
    """Split the text into sections of approximately equal length."""
    words = text.split()
    sections = []
    start = 0
    while start < len(words):
        end = start + words_per_section
        if end >= len(words):
            sections.append(' '.join(words[start:]))
            break
        last_sentence_end = start
        for i in range(start, min(end, len(words))):
            if words[i].endswith(('.', '!', '?')) and i > last_sentence_end:
                last_sentence_end = i + 1
        if last_sentence_end == start:
            last_sentence_end = end
        sections.append(' '.join(words[start:last_sentence_end]))
        start = last_sentence_end
    return sections

def parse_epub(file, use_text_chunking, section_count):
    """Parse an EPUB file and extract its content."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        book = epub.read_epub(tmp_file_path)
        sections = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                title = soup.find(['h1', 'h2', 'h3', 'title'])
                title_text = title.text.strip() if title else f"Section {len(sections) + 1}"
                main_content = soup.get_text().strip()
                if main_content:
                    sections.append((title_text, main_content))
        
        if not use_text_chunking and len(sections) >= section_count:
            logging.info(f"Using {len(sections)} detected sections for EPUB parsing")
            return sections
        else:
            logging.info("Falling back to text chunking for EPUB")
            full_text = "\n\n".join([content for _, content in sections])
            chunked_sections = split_into_sections(full_text)
            return [(f"Section {i+1}", section) for i, section in enumerate(chunked_sections)]
    finally:
        os.unlink(tmp_file_path)

def parse_book_content(content, file_type, section_count):
    """Parse book content and extract sections."""
    soup = BeautifulSoup(content, 'html.parser')
    logging.info(f"Parsing {file_type} content")
    
    chapter_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title']
    chapter_classes = ['chapter']
    chapter_patterns = re.compile(r'chapter|book|section|part|\d+', re.IGNORECASE)

    sections = []
    for tag in soup.find_all(chapter_tags + [{'class': chapter_classes}]):
        title = tag.get_text().strip()
        if chapter_patterns.search(title) or tag.name in chapter_tags:
            content = ''
            for sibling in tag.find_next_siblings():
                if sibling.name in chapter_tags or sibling.get('class') and any(cls in chapter_classes for cls in sibling.get('class', [])):
                    break
                content += sibling.get_text() + '\n'
            if content.strip():
                sections.append((title, content.strip()))

    if len(sections) >= section_count:
        logging.info(f"Using {len(sections)} detected sections for {file_type} parsing")
        return sections
    else:
        logging.info(f"Falling back to text chunking for {file_type}")
        full_text = soup.get_text()
        text_sections = split_into_sections(full_text)
        return [(f"Section {i+1}", section) for i, section in enumerate(text_sections)]

def parse_mobi(file, use_text_chunking, section_count):
    """Parse a MOBI file and extract its content."""
    # Note: This function is a placeholder and needs to be implemented
    st.error("MOBI parsing is not yet implemented. Please convert to EPUB and try again.")
    return []

def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return ''.join(c for c in filename if c.isalnum() or c in (' ', '_')).strip()

def clean_text_formatting(text):
    """Clean up text formatting for better TTS output."""
    def is_letter(char):
        return char.isalpha()

    tokens = re.findall(r"\w+|[^\w\s]|\s+", text)

    cleaned_tokens = []
    for i, token in enumerate(tokens):
        if token in ".,!?;:\"'":
            prev_char = tokens[i-1][-1] if i > 0 else ' '
            next_char = tokens[i+1][0] if i < len(tokens) - 1 else ' '

            if token == "'" and is_letter(prev_char) and is_letter(next_char):
                cleaned_tokens.append(token)
            elif next_char not in ".,!?;:\"'":
                cleaned_tokens.append(f"{token} ")
            elif prev_char not in ".,!?;:\"'":
                cleaned_tokens.append(f" {token}")
            else:
                cleaned_tokens.append(token)
        else:
            cleaned_tokens.append(token)

    cleaned_text = ''.join(cleaned_tokens)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    cleaned_text = re.sub(r'(?<=\w)\s+(?=[.,!?;:])', '', cleaned_text)
    cleaned_text = re.sub(r'(?<=[.,!?;:])\s+(?=\w)', ' ', cleaned_text)
    cleaned_text = re.sub(r"(?<=\w)'(?=\w)", "'", cleaned_text)
    
    return cleaned_text.strip()

def generate_output_file(text, selected_voice, book_name, section_index, chunk_index):
    """Generate an audio file using Piper TTS."""
    model_path = f'"{VOICES_FOLDER}{selected_voice}"'
    
    sanitized_book_name = sanitize_filename(book_name)
    book_output_folder = os.path.join(OUTPUT_FOLDER, sanitized_book_name)
    os.makedirs(book_output_folder, exist_ok=True)

    output_file_name = f"{sanitized_book_name}_{section_index+1:02d}.wav"
    output_file_path = os.path.join(book_output_folder, output_file_name)

    quoted_output_path = shlex.quote(output_file_path)

    command = [
        PIPER_LOCATION,
        "--cuda",
        "--model", model_path,
        "--output_file", quoted_output_path
    ]
    
    full_command = f"echo {shlex.quote(text)} | {' '.join(command)}"
    
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        logging.error(f"Error generating audio: {result.stderr}")
        return None

    logging.info(f"Generated audio file: {output_file_path}")
    return output_file_path

def main():
    st.title("Audiobook Creator")
    
    use_text_chunking = st.checkbox("Use text chunking instead of chapters")
    section_count = st.number_input("Minimum number of sections for chapter-based parsing", min_value=1, value=4)
    uploaded_file = st.file_uploader("Choose an epub or mobi file", type=["epub", "mobi"])
    
    if uploaded_file is not None:
        book_name = os.path.splitext(uploaded_file.name)[0]
        if uploaded_file.name.lower().endswith('.epub'):
            sections = parse_epub(uploaded_file, use_text_chunking, section_count)
        elif uploaded_file.name.lower().endswith('.mobi'):
            sections = parse_mobi(uploaded_file, use_text_chunking, section_count)
        else:
            st.error("Unsupported file format. Please upload an EPUB or MOBI file.")
            return

        st.subheader("Select sections to include")
        
        select_all = st.checkbox("Select All")
        
        selected_sections = []
        for i, (title, content) in enumerate(sections):
            if select_all or st.checkbox(f"{title}", key=f"section_{i}"):
                cleaned_content = clean_text_formatting(content)
                content = st.text_area(f"Content Preview ({title})", cleaned_content, height=200, key=f"content_{i}")
                selected_sections.append((title, content))

        valid_voices = sorted([f for f in os.listdir(VOICES_FOLDER) if f.endswith('.onnx')])
        selected_voice = st.selectbox("Select Voice:", valid_voices)

        use_custom_naming = st.checkbox("Use custom naming for output folder/files")
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
                output_file = generate_output_file(content, selected_voice, book_name, i, 0)
                if output_file is None:
                    st.error(f"Failed to generate audio for {title}")
                else:
                    st.success(f"Generated: {output_file}")
                progress = (i + 1) / len(selected_sections)
                progress_bar.progress(progress)
                status_text.text(f"Processing: {title}")
            st.success("Audiobook generation completed!")

if __name__ == "__main__":
    main()
