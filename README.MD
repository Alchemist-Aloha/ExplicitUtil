# explicit_util

A utility library for managing media files, especially focused on conversion, organization, and archival.

## Overview

This library provides tools for managing media content, with features for video transcription, image conversion, file renaming, zip operations, and more. It's designed to help organize and process large media collections efficiently.

## Features

- Batch convert images to WebP format
- Transcribe videos using whisper.cpp
- Recursively rename video files using namer
- Zip and archive content with backup functionality
- Batch unzip operations with recursive support
- Generate and batch add metadata entry for media files

## Installation

### Install [namer](https://github.com/ThePornDatabase/namer)

```bash
pip install namer
```

Fill your PornDB API into `.namer.cfg`.

### Install [ImageMagick](https://imagemagick.org/script/download.php)

Download the installer and install.

### Install [whisper.cpp](https://github.com/ggerganov/whisper.cpp)

Compile the code based on your inference hardware.

### Install `explicit_util`

```bash
git clone https://github.com/Alchemist-Aloha/explicit_util.git
cd explicit_util
pip install -e .
```

## Usage

### Using Jupyter Notebook

You can run the code in Jupyter Notebook. The library is designed to be used interactively, allowing you to test and modify the code as needed. See `explicit_util_examples.ipynb`

### Using Command Line

You can run the code from the command line.

```bash
# Transcribe videos
python -m explicit_util.whisper_cpp_transcribe
# Convert images to WebP
python -m explicit_util.convert_pic_to_webp
# Zip and archive pictures
python -m explicit_util.zip_and_move
# Unzip and extract
python -m explicit_util.recursive_unzip
# Generate metadata
python -m explicit_util.nfo_tool
# Batch add metadata using namer
python -m explicit_util.recursive_namer
```

## License

MIT
