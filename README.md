# Audiobook Creator

This repository contains a Streamlit web application that converts EPUB files into audiobooks using Text-to-Speech (TTS) technology. **Note that MOBI file parsing is not yet implemented but is planned (you can convert and upload if you're desperate)**.

Audiobook Creator uses the local neural text-to-speech (TTS) system called [**Piper**](https://github.com/rhasspy/piper). 

## Features

- Upload EPUB files and convert them into audiobooks.
- Select specific sections of the book to include in the audiobook.
- Choose from various voice models for the narration.
- Supports custom naming for output files and folders.

## Installation

### Prerequisites/Installation and Setup

- Python 3.7 or higher
- `pip` (Python package installer)

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

    Get the Piper TTS release for your system from [Piper's official repository](https://github.com/rhasspy/piper) and put the piper folder at `./piper`

   The populate the `./static/voices` folder with your chosen voice model files from [Hugging Face](https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0).

   ## **You must have *.onnx* and *.json* files for any given voice. If these are not both present, the voice will not be available in the web app. Piper requires that voice models use the following format:**

   ```
   NAME.onnx
   NAME.onnx.json
   ```
   **You will note that [Hugging Face](https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0) does not provide names in this naming format and you will need to rename the files.**

   I recommend the "[en_US-libritts_r-medium](https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/en/en_US/libritts_r/medium)" voice model for a clear English-speaking voice. 

4. Configuration settings for the TTS application are located in the `configuration.py` file. Ensure that the paths to the voices folder, output folder, and the location of the Piper executable is correctly set (**you may need to include filetypes in windows, I do not have a windows system to test this**):

```
VOICES_FOLDER = "./static/voices/"
OUTPUT_FOLDER = "./static/output/"
PIPER_LOCATION = "./piper/piper"
```
****

5. **Run the Streamlit app:**

    ```
    streamlit run app.py
    ```

## Usage

1. **Upload an EPUB file:**
    - Click on the "Choose an epub file" button and upload your EPUB file.

2. **Select sections to include:**
    - Check the sections you want to include in the audiobook. You can alter the text included in these if there are errors or adjustments you want to make.

3. **Select a voice model:**
    - Choose a voice model from the dropdown list.

4. **Generate the audiobook:**
    - Click the "Generate Audiobook" button to start the conversion process.

The generated audiobook files will be saved in the specified output folder.



