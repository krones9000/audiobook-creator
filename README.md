# Audiobook Creator

This repository contains a Streamlit web application that converts EPUB files into audiobooks using Text-to-Speech (TTS) technology. 

Audiobook Creator uses the local neural text-to-speech (TTS) system called [**Piper**](https://github.com/rhasspy/piper).

Knowing exactly how to segement an ebook is non-trivial. I've implemented two approaches here that work to varying degree (and seem to work better on epubs).

Essentially, the app looks for markers typically used to indicate chapters and tries to segment on chapters. If it can't detect chapters, or if the chapter count is low (set on the page but defaulting to 4), suggesting the book might be incorrectly formatted as one single large chapter, then it will default to a text chunking approach. Currently that chunking works on chunks of approximately 10,000 words (to the nearest sentence). However, you can change this in the app.py if you'd like smaller chunks (to make editting any mistakes easier) or if you want more granualirity of files/generations by editting `words_per_section` on line 21.

<p align="center">
<img src="https://github.com/user-attachments/assets/d24e7931-2bc0-4665-a2eb-93085d1793f8" width="500" title="Showing what the interface looks like after completing a BPM change on a folder."/>
</p>


## Features

- Upload EPUB files and convert them into audiobooks.
- Select specific sections of the book to include in the audiobook.
- Choose from various voice models for the narration.
- Supports custom naming for output files and folders.
- Text chunking option for better handling of books without clear chapter divisions.
- Configurable minimum section count for chapter-based parsing.

## Installation

### Prerequisites

- Python 3.7 or higher
- `pip` (Python package installer)

### Setup

1. **Clone the repository:**

   ```
   git clone https://github.com/krones9000/audiobook-creator.git
   cd audiobook-creator
   ```

2. **Install the required packages:**

   ```
   pip install streamlit ebooklib beautifulsoup4 lxml
   ```

3. **Set up the Piper TTS system:**

   Download the Piper TTS release for your system from [Piper's official repository](https://github.com/rhasspy/piper) and place the piper folder at `./piper`.

   Populate the `./static/voices` folder with your chosen voice model files from [Hugging Face](https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0).

   **Important:** You must have both *.onnx* and *.json* files for any given voice. The files should be named as follows:

   ```
   NAME.onnx
   NAME.onnx.json
   ```

   Note that you may need to rename the files downloaded from Hugging Face to match this format.

   I recommend the "[en_US-libritts_r-medium](https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/en/en_US/libritts_r/medium)" voice model for a clear English-speaking voice.

4. **Configuration:**

   The configuration settings are now included directly in the `app.py` file. Ensure that the following variables are set correctly at the beginning of the file:

   ```python
   VOICES_FOLDER = "./static/voices/"
   OUTPUT_FOLDER = "./static/output/"
   PIPER_LOCATION = "./piper/piper"
   ```

   Note: On Windows systems, you may need to include file extensions in the `PIPER_LOCATION` path.

5. **Run the Streamlit app:**

   ```
   streamlit run app.py
   ```

## Usage

1. **Upload an EPUB or MOBI file:**
   - Click on the "Choose an epub/mobi file" button and upload your ebook file.

2. **Configure parsing options:**
   - Check the "Use text chunking instead of chapters" box if your book doesn't have clear chapter divisions.
   - Set the "Minimum number of sections for chapter-based parsing" to control when the app switches to text chunking (useful if chapters are present but not correct).

3. **Select sections to include:**
   - Check the sections you want to include in the audiobook. You can edit the text if needed.

4. **Select a voice model:**
   - Choose a voice model from the dropdown list.

5. **Custom naming (optional):**
   - Check the "Use custom naming for output folder/files" box to specify a custom name for the output if you want to. Remember this is a folder name so no crazy characters.

6. **Generate the audiobook:**
   - Click the "Generate Audiobook" button to start the conversion process (This can take some time for long items but piper is overall very fast and **can create about an hour of audio in around 5-10 minutes** depending on your system.

The generated audiobook files will be saved in the specified output folder within the `./static/output` folder.

## Troubleshooting

If you encounter any issues, please check the console output for error messages. Make sure all dependencies are correctly installed and the Piper TTS system is located properly and correct for your system.

## Contributing

Contributions to improve the Audiobook Creator are welcome. Please feel free to submit pull requests or open issues for bugs and feature requests.
