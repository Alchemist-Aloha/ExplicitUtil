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

```bash
git clone https://github.com/yourusername/explicit_util.git
cd explicit_util
pip install -e .
# or
poetry add explicit-util
```

## Usage

```python
import explicit_util

# Example content analysis
result = explicit_util.analyze(content)
if result.is_sensitive:
    # Handle accordingly
    pass
```

## License

MIT