# ExplicitUtil

A utility library for managing media files, especially focused on conversion, organization, and archival.

## Overview

This library provides tools for managing media content, with features for video transcription, image conversion, file renaming, zip operations, and more. It's designed to help organize and process large media collections efficiently.

## Features

- **Batch convert images to WebP format**  
    Use `convert-pic` to convert image files to the WebP format, reducing file size while maintaining quality.
- **Transcribe videos using whisper.cpp**  
    `transcribe` leverages whisper.cpp to generate accurate transcriptions for video files.
- **Recursively rename video files using namer**  
    `rename` integrates with the [namer](https://github.com/ThePornDatabase/namer) library to rename video files in bulk.
- **Zip and archive content**  
    `archive` allows you to compress and archive folders into zip files asynchronously.
- **Batch unzip operations**  
    `unzip` enables you to extract zip files recursively, with an option to delete archives after extraction.
- **Generate and batch add metadata (.nfo)**  
    `nfo` and related tools (`nfo-tag`, `nfo-studio`, `nfo-actor`) create and modify metadata files for media content.
- **Group files by regex**  
    `group` organizes files into subdirectories based on regex pattern matching (e.g., grouping by date).
- **Merge video files**  
    `merge` combines multiple video files into a single output using ffmpeg.
- **Remove empty folders**  
    `remove-empty` cleans up directory structures by recursively deleting empty folders.

## Installation

### Prerequisites

- **[uv](https://github.com/astral-sh/uv)** (Recommended) or **pip**
- **[ImageMagick](https://imagemagick.org/)** for image conversion.
- **[whisper.cpp](https://github.com/ggerganov/whisper.cpp)** compiled locally for transcription.
- **ffmpeg** for video merging.

### Install `ExplicitUtil`

**Recommended (using uv):**

```bash
git clone https://github.com/Alchemist-Aloha/ExplicitUtil.git
cd ExplicitUtil
uv sync
```

**Using pip:**

```bash
pip install -e .
```

## Configuration

ExplicitUtil supports persisting your preferred settings (like `whisper_root`, `num_threads`, etc.) to a local configuration file.

- **Location:** `~/.explicitutil/*.toml`
- **Usage:** Add the `--save` flag to any command to persist the provided options for future use.

Example:
```bash
ExplicitUtil transcribe ./my_videos --whisper-root /path/to/whisper.cpp --save
```
Next time, you can just run:
```bash
ExplicitUtil transcribe ./other_videos
```

## Usage

### Command Line Interface

The primary way to use ExplicitUtil is via the CLI entry point.

```bash
# Get help and list all commands
ExplicitUtil --help

# Transcribe videos
ExplicitUtil transcribe [FOLDER] --whisper-root [PATH]

# Convert images to WebP
ExplicitUtil convert-pic [FOLDER] --quality 80

# Zip and archive folders
ExplicitUtil archive [SOURCE] [DESTINATION]

# Unzip and extract
ExplicitUtil unzip [FOLDER] --delete

# Generate metadata
ExplicitUtil nfo [MEDIA_PATH]

# Batch add tag to NFO files
ExplicitUtil nfo-tag [NFO_DIR] "MyTag"

# Batch rename video files using namer
ExplicitUtil rename [FOLDER]

# Group files by date (default regex)
ExplicitUtil group [DIRECTORY] --move

# Merge videos
ExplicitUtil merge file1.mp4 file2.mp4 output.mp4

# Remove empty folders
ExplicitUtil remove-empty [TARGET_DIR]
```

### API Documentation

Check [https://alchemist-aloha.github.io/ExplicitUtil/ExplicitUtil.html](https://alchemist-aloha.github.io/ExplicitUtil/ExplicitUtil.html) for the full API documentation.

### Using Jupyter Notebook

See `explicit_util_examples.ipynb` for interactive examples and library usage.

## License

MIT
