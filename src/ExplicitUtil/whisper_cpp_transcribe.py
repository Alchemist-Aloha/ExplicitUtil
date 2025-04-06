import subprocess
from pathlib import Path
import threading
import queue
import concurrent.futures

# Global whisper job queue
whisper_queue = queue.Queue()


def get_input_folder() -> tuple[Path, Path]:
    """Prompt user for input folder and whisper root directory.
    Returns:
        tuple: A tuple containing the input folder and whisper root directory.
    """
    while True:
        input_folder = Path(
            input("Enter the path to the folder containing video files: ").strip("\"")
        )
        whisper_root = Path(input("Enter the path to the whisper.cpp folder: ").strip("\""))
        if input_folder.exists() and whisper_root.exists():
            return input_folder, whisper_root
        print(
            f"The folder '{input_folder}' or '{whisper_root}' does not exist. Please enter a valid folder path."
        )


def extract_audio(video_file: Path, whisper_root: Path, prompt: str = "") -> None:
    """Extract audio using FFmpeg concurrently.
    If successful, put the whisper job into the whisper_queue for sequential processing.
    """
    input_folder = video_file.parent
    base_name = video_file.stem
    audio_file = input_folder / f"{base_name}.wav"
    whisper_path = whisper_root / "build/bin/Release/whisper-cli.exe"
    model_path = whisper_root / "models/ggml-large-v3.bin"

    print(f"[FFmpeg] Processing: {video_file}")

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_file),  # input video file, overwrite if exists
        "-af",
        "highpass=200,lowpass=3000,afftdn,dialoguenhance",  # audio filters, voice enhancement
        "-ar",
        "16000",
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(audio_file),  # output audio file
    ]
    print(f"[FFmpeg] Running command: {' '.join(ffmpeg_cmd)}")
    try:
        process = subprocess.run(ffmpeg_cmd, text=True, capture_output=True)
        print(f"[FFmpeg] Audio extraction completed for {video_file}.")
        print(process.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[FFmpeg] Error processing {video_file}: {e.stderr}")
        return

    # When ffmpeg extraction is successful, push a whisper job to the queue.
    job = {
        "video_file": video_file,
        "audio_file": audio_file,
        "input_folder": input_folder,
        "base_name": base_name,
        "whisper_path": whisper_path,
        "model_path": model_path,
        "prompt": prompt,
    }
    whisper_queue.put(job)
    print(f"[FFmpeg] Extraction completed for {video_file}. Whisper job queued.")


def whisper_worker() -> None:
    """Continuously process whisper jobs sequentially."""
    while True:
        job = whisper_queue.get()
        if job is None:  # Sentinel to shutdown the worker
            break

        video_file = job["video_file"]
        audio_file = job["audio_file"]
        input_folder = job["input_folder"]
        base_name = job["base_name"]
        whisper_path = job["whisper_path"]
        model_path = job["model_path"]
        prompt = job["prompt"]

        print(f"[Whisper] Processing: {video_file}")

        whisper_cmd = [
            str(whisper_path),
            "-m",
            str(model_path),
            "-t",
            "4",
            "--max-context",
            "0",
            "-tr",
            "true",
            "--logprob-thold",
            "-0.5",
            "--no-speech-thold",
            "0.3",
            "--word-thold",
            "0.5",
            "--best-of",
            "5",
            "-l",
            "auto",
            "-et",
            "2.8",
            "-osrt",
            "--prompt",
            prompt,
            "-f",
            str(audio_file),
            "-of",
            str(input_folder / base_name),
        ]
        print(f"[Whisper] Running command: {' '.join(whisper_cmd)}")
        try:
            process = subprocess.run(whisper_cmd, text=True, capture_output=True)
            print(f"[Whisper] Transcription completed for {video_file}.")
            print(process.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[Whisper] Error processing {video_file}: {e.stderr}")
            whisper_queue.task_done()
            continue

        # Remove temporary audio file
        try:
            audio_file.unlink()
            print(f"[Whisper] Removed temporary audio file {audio_file}")
        except Exception as e:
            print(f"[Whisper] Could not remove audio file {audio_file}: {e}")

        whisper_queue.task_done()


def process_videos(
    input_folder: str | Path,
    whisper_root: str | Path,
    prompt: str = "",
    suffix: tuple[str, ...] = (".m4v", ".mp4", ".mkv"),
) -> None:
    """Process all video files in the input folder.
    Args:
        input_folder (Path or str): Folder containing video files.
        whisper_root (Path or str): Path to the whisper.cpp root directory.
        prompt (str): Prompt for Whisper transcription.
        suffix (tuple[str]): Extensions to process.
    """
    input_folder = Path(input_folder)
    whisper_root = Path(whisper_root)
    if not input_folder.exists():
        print(f"Error: Directory '{input_folder}' not found.")
        return
    if not whisper_root.exists():
        print(f"Error: Directory '{whisper_root}' not found.")
        return

    # Start whisper worker thread
    worker_thread = threading.Thread(target=whisper_worker, daemon=True)
    worker_thread.start()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for video_file in input_folder.rglob("*"):
            if video_file.suffix.lower() in suffix:
                futures.append(
                    executor.submit(extract_audio, video_file, whisper_root, prompt)
                )
        # Wait for all ffmpeg extraction jobs to complete
        concurrent.futures.wait(futures)

    # Wait until all whisper jobs are done
    whisper_queue.join()

    # Stop the whisper worker
    whisper_queue.put(None)
    worker_thread.join()

    print(f"Transcription completed for all videos in '{input_folder}'.")


def run_batch_transcribe(
    input_folder: str | Path,
    whisper_root: str | Path,
    prompt: str = "",
    suffix: tuple[str, ...] = (".m4v", ".mp4", ".mkv"),
) -> None:
    """Main loop prompting for input folders and processing videos."""
    global whisper_queue
    whisper_queue = queue.Queue()
    while True:
        process_videos(input_folder, whisper_root, prompt, suffix)


if __name__ == "__main__":
    while True:
        input_folder, whisper_root = get_input_folder()
        suffix = input(
            "Enter the file extensions to process (comma-separated, e.g., .m4v,.mp4): "
        )
        suffix = tuple(ext.strip() for ext in suffix.split(","))
        prompt = input(
            "Enter the prompt for Whisper transcription (leave blank for none): "
        )
        if not prompt:
            prompt = ""
        process_videos(input_folder, whisper_root, prompt="", suffix=(".m4v",))
