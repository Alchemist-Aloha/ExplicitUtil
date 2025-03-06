# explicit_util

A utility library for managing media files, especially focused on conversion, organization, and archival.

## Overview

This library provides tools for managing media content, with features for video transcription, image conversion, file renaming, zip operations, and more. It's designed to help organize and process large media collections efficiently.

## Features

- Convert HEIC images to WebP format
- Transcribe videos using whisper.cpp
- Recursively rename video files using namer
- Zip and archive content with backup functionality
- Batch unzip operations with recursive support

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

See `explicit_util_examples.ipynb`

## License

MIT