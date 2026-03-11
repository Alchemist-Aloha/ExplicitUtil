# ExplicitUtil

A utility library for managing media files, especially focused on conversion, organization, and archival.

## Overview

This library provides tools for managing media content, with features for video transcription, image conversion, file renaming, zip operations, and more. It's designed to help organize and process large media collections efficiently.

## Features

- **Batch convert images to WebP format**  
    Use `convert_pic_to_webp.py` to convert image files to the WebP format, reducing file size while maintaining quality. This is useful for optimizing storage and web usage.

- **Transcribe videos using whisper.cpp**  
    `whisper_cpp_transcribe.py` leverages the whisper.cpp library to generate accurate transcriptions for video files. Ideal for creating subtitles or searchable text content.

- **Recursively rename video files using namer**  
    `recursive_namer.py` integrates with the namer library to rename video files in bulk, ensuring consistent and organized naming conventions.

- **Zip and archive content with backup functionality**  
    `zip_and_move.py` allows you to compress and archive media files into zip files, with options for creating backups to ensure data safety.

- **Batch unzip operations with recursive support**  
    `recursive_unzip.py` enables you to extract zip files in bulk, handling nested zip files automatically for efficient processing.

- **Generate and batch add metadata entry for media files**  
    Use `nfo_tool.py`t to create metadata files for your media content. This is particularly useful for cataloging and organizing large collections.

## Installation

### Prerequisites

#### Install [namer](https://github.com/ThePornDatabase/namer) to use `recursive_namer.py`

```bash
pip install namer
```

Fill your API key into `.namer.cfg`.

#### Install [ImageMagick](https://imagemagick.org/script/download.php) to use `convert_pic_to_webp.py`

Download the installer and install.

#### Install [whisper.cpp](https://github.com/ggerganov/whisper.cpp) to use `whisper_cpp_transcribe.py`

Compile the code based on your inference hardware.

### Install `ExplicitUtil`

**Recommended (using [uv](https://github.com/astral-sh/uv)):**

```bash
git clone https://github.com/Alchemist-Aloha/ExplicitUtil.git
cd ExplicitUtil
uv sync
```

**Using pip:**

```bash
pip install -e .
```

## Usage

### API Documentation
The library is designed to be used as a module, and the functions are organized into separate files for clarity. Each file contains a specific set of functions related to its purpose.

Check [https://alchemist-aloha.github.io/ExplicitUtil/ExplicitUtil.html](https://alchemist-aloha.github.io/ExplicitUtil/ExplicitUtil.html) for the API documentation.

### Using Jupyter Notebook

You can run the code in Jupyter Notebook. The library is designed to be used interactively, allowing you to test and modify the code as needed. See `explicit_util_examples.ipynb`

### Using Command Line

You can run the code from the command line using the `ExplicitUtil` entry point or as a module.

```bash
# Get help
ExplicitUtil --help

# Transcribe videos
ExplicitUtil transcribe [FOLDER]
# Convert images to WebP
ExplicitUtil convert-pic [FOLDER]
# Zip and archive folders
ExplicitUtil archive [SOURCE] [DESTINATION]
# Unzip and extract
ExplicitUtil unzip [FOLDER]
# Generate metadata
ExplicitUtil nfo [MEDIA_PATH]
# Batch add metadata using namer
ExplicitUtil rename [FOLDER]
# Remove empty folders
ExplicitUtil remove-empty [TARGET_DIR]
# Group files
ExplicitUtil group [DIRECTORY]
# Merge videos
ExplicitUtil merge [VIDEO_FILES]... [OUTPUT_FILE]
```

Alternatively, using `python -m`:

```bash
python -m ExplicitUtil.whisper_cpp_transcribe
python -m ExplicitUtil.convert_pic_to_webp
# ... and so on
```

## License

MIT
