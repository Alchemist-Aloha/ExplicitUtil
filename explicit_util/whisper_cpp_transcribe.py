# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path

# whisper_root = Path(r"E:\whisper.cpp")
# model_path = whisper_root / "models/ggml-large-v3.bin"

def get_input_folder() -> tuple[Path, Path]:
    """Prompt user for input folder and whisper root directory.
    Returns:
        tuple: A tuple containing the input folder and whisper root directory.
    """
    while True:
        input_folder = Path(input("Enter the path to the folder containing video files: "))
        whisper_root = Path(input("Enter the path to the whisper.cpp folder: "))
        if input_folder.is_dir() and whisper_root.is_dir():
            return input_folder, whisper_root
        print(f"The folder '{input_folder}' or '{whisper_root}' does not exist. Please enter a valid folder path.")

def process_single_video(video_file: Path, whisper_root: Path, prompt: str = "") -> None:
    """ Process a single video file to extract audio and transcribe it using Whisper.cpp.
    Args:
        video_file (Path): Path to the video file.
        whisper_root (Path): Path to the whisper.cpp root directory.
        prompt (str): Prompt for Whisper.cpp transcription.
    """
    input_folder = video_file.parent
    base_name = video_file.stem
    audio_file = input_folder / f"{base_name}.wav"
    # srt_file = input_folder / f"{base_name}.srt"
    whisper_path = whisper_root / "build/bin/Release/whisper-cli.exe"
    model_path = whisper_root / "models/ggml-large-v3.bin"
    
    print(f"Processing: {video_file}")
    
    # Extract audio using FFmpeg
    ffmpeg_cmd = [
        "ffmpeg", "-i", str(video_file),
        "-af", "highpass=200,lowpass=3000,afftdn,dialoguenhance",
        "-ar", "16000", "-ac", "2", "-c:a", "pcm_s16le", str(audio_file)
    ]
    print(f"Running command: {' '.join(ffmpeg_cmd)}")
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        print(line, end='')

    process.wait()
    # Transcribe audio using Whisper.cpp
    whisper_cmd = [
        str(whisper_path), "-m", str(model_path),
        "-t", "4", "--max-context", "0", "-tr", "true",
        "--logprob-thold", "-0.5", "--no-speech-thold", "0.3", "--word-thold", "0.5",
        "--best-of", "5", "-l", "auto", "-et", "2.8", "-osrt",
        "--prompt", prompt, "-f", str(audio_file), "-of", str(input_folder / base_name)
    ]
    print(f"Running command: {' '.join(whisper_cmd)}")
    
    # Run the Whisper command and print output in real-time
    process = subprocess.Popen(whisper_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in process.stdout:
        print(line, end='')

    process.wait()
    
    # Remove temporary audio file
    audio_file.unlink()

def process_videos(input_folder: str, whisper_root: Path, prompt:str="", suffix:tuple[str]=(".m4v",".mp4",".mkv")) -> None:
    """Process all video files in the input folder.
    Args:
        input_folder (Path or str): Path to the folder containing video files.
        whisper_root (Path): Path to the whisper.cpp root directory.
        prompt (str): Prompt for Whisper.cpp transcription.
        suffix (tuple[str]): Tuple of file extensions to process.
    """
    input_folder = Path(input_folder)
    if not input_folder.exists():
        print(f"Error: Directory '{input_folder}' not found.")
        return
    for video_file in input_folder.rglob("*"):
        if video_file.suffix.lower() in suffix:
            process_single_video(video_file, whisper_root, prompt)
    
    print(f"Transcription completed for all videos in '{input_folder}'.")

if __name__ == "__main__":
    while True:
        folder, whisper_root = get_input_folder()
        process_videos(folder, whisper_root, prompt="", suffix=(".m4v"))
