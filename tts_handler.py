"""
Piper TTS functionality for audiobook creation.

Author: Kieran Currie Rones
Date: July 22nd, 2024

This module contains the generation route for TTS.
"""

import subprocess
import shlex
import os
from configuration import VOICES_FOLDER, OUTPUT_FOLDER, PIPER_LOCATION

def generate_output_file(text, selected_voice, book_name, section_index, chunk_index):
    model_path = f'"{VOICES_FOLDER}{selected_voice}"'
    
    # Create a sanitized version of the book name for the folder
    sanitized_book_name = ''.join(c for c in book_name if c.isalnum() or c in (' ', '_')).rstrip()
    book_output_folder = os.path.join(OUTPUT_FOLDER, sanitized_book_name)
    os.makedirs(book_output_folder, exist_ok=True)

    # Create the output file name with proper indexing and extension
    output_file_name = f"{sanitized_book_name}_{section_index+1:02d}.wav"
    output_file_path = os.path.join(book_output_folder, output_file_name)

    # Ensure the output path is properly quoted
    quoted_output_path = shlex.quote(output_file_path)

    command = [
        PIPER_LOCATION,
        "--cuda",
        "--model", model_path,
        "--output_file", quoted_output_path
    ]
    
    # Join the command parts and use shell=True
    full_command = f"echo {shlex.quote(text)} | {' '.join(command)}"
    
    # Run the command and capture output
    result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
    
    # Check if the command was successful
    if result.returncode != 0:
        print(f"Error generating audio: {result.stderr}")
        return None

    print(f"Generated audio file: {output_file_path}")
    return output_file_path
