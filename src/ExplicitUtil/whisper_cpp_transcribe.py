import subprocess
from pathlib import Path
import threading
import queue
import concurrent.futures
import sys
import importlib.resources
import toml
__docformat__ = "google"
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
        subprocess.run(ffmpeg_cmd, text=True, capture_output=True)
        print(f"[FFmpeg] Audio extraction completed for {video_file}.")
        # print(process.stdout)
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
    config_path = str(importlib.resources.files('ExplicitUtil').joinpath('config/whisper_command.toml'))
    if not Path(config_path).exists():
        print(f"Error: Whisper.cpp command config '{config_path}' not found. Generate default config.")
        command = {
            "threads" : 4,
            "max_context" : 0,
            "translate" : True,
            "logprob_thold" : -0.5,
            "no_speech_thold" : 0.3,
            "word_thold" : 0.5,
            "best_of" : 5,
            "language" : "auto",
            "entropy-thold" : 2.8,
            "output_format" : "-osrt",
        }
        with open(config_path, 'w') as f:
            f.write(toml.dumps(command))
    else:
        with open(config_path, 'r') as f:
            command = toml.load(f)
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

        cli_encoding = 'utf-8'
        print(f"[Whisper] Processing: {video_file}")

        whisper_cmd = [
            str(whisper_path),
            "-m",
            str(model_path),
            "--threads",
            str(command["threads"]),
            "--max-context",
            str(command["max_context"]),
            "--translate",
            str(command["translate"]),
            "--logprob-thold",
            str(command["logprob_thold"]),
            "--no-speech-thold",
            str(command["no_speech_thold"]),
            "--word-thold",
            str(command["word_thold"]), 
            "--best-of",
            str(command["best_of"]),
            "--language",
            str(command["language"]),
            "--entropy-thold",
            str(command["entropy-thold"]),
            str(command["output_format"]),
            "--prompt",
            prompt,
            "-f",
            str(audio_file),
            "-of",
            str(input_folder / base_name),
        ]

        print(f"[Whisper] Running command: {' '.join(whisper_cmd)}")
        # try:
        #     process = subprocess.run(whisper_cmd, text=True, capture_output=True)
        #     print(f"[Whisper] Transcription completed for {video_file}.")
        #     print(process.stdout)
        # except subprocess.CalledProcessError as e:
        #     print(f"[Whisper] Error processing {video_file}: {e.stderr}")
        #     whisper_queue.task_done()
        #     continue

        # # Remove temporary audio file
        # try:
        #     audio_file.unlink()
        #     print(f"[Whisper] Removed temporary audio file {audio_file}")
        # except Exception as e:
        #     print(f"[Whisper] Could not remove audio file {audio_file}: {e}")

        # whisper_queue.task_done()
        process = None  # Initialize process variable for cleanup
        success = False  # Initialize success variable
        try:
            # --- Start Subprocess with Popen ---
            process = subprocess.Popen(
                whisper_cmd,
                stdout=subprocess.PIPE,    # Capture stdout
                stderr=subprocess.STDOUT,  # Redirect stderr TO stdout stream
                text=True,                 # Decode output as text
                encoding=cli_encoding,     # Specify expected encoding
                errors='replace',          # How to handle decoding errors
                bufsize=1,                 # Use line buffering
                shell=False                # Do NOT use shell=True unless essential
                                           # (security risk, quoting issues)
            )

            # --- Read and Display Output in Real-Time ---
            print(f"--- [Whisper Output Start: {base_name}] ---")
            # Read line by line until the process's stdout stream is closed
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    sys.stdout.write(line)  # Write the line directly
                    sys.stdout.flush()      # Ensure it appears immediately
            print(f"\n--- [Whisper Output End: {base_name}] ---") # Add newline for clarity

            # --- Wait for Process Completion and Check Result ---
            process.wait() # Wait for the process to fully terminate
            return_code = process.returncode

            if return_code == 0:
                print(f"[Whisper] Transcription completed successfully for {video_file} (Exit Code: {return_code}).")
                success = True
            else:
                # Error message from Whisper was already printed in real-time
                print(f"[Whisper] Error: Whisper process for {video_file} failed with Exit Code: {return_code}", file=sys.stderr)
                success = False

        except FileNotFoundError:
            print(f"[Whisper] Error: Whisper executable not found at '{whisper_path}'. Cannot process {video_file}.", file=sys.stderr)
            # No process started, job failed. Ensure success remains False.
            success = False
        except Exception as e:
            print(f"[Whisper] An unexpected error occurred while running/reading Whisper for {video_file}: {e}", file=sys.stderr)
            success = False
            # --- Attempt to Terminate Zombie Process (if any) ---
            if process and process.poll() is None: # Check if process exists and is running
                 print("[Whisper] Attempting to terminate Whisper process.", file=sys.stderr)
                 try:
                     process.terminate() # Ask nicely first
                     process.wait(timeout=5) # Give it time to exit
                     print("[Whisper] Process terminated.", file=sys.stderr)
                 except subprocess.TimeoutExpired:
                     print("[Whisper] Process did not terminate gracefully, killing.", file=sys.stderr)
                     process.kill() # Force kill
                     process.wait() # Wait for kill to complete
                 except Exception as term_e:
                     print(f"[Whisper] Error during process termination: {term_e}", file=sys.stderr)
        finally:
            # --- Cleanup ---
            if success:
                # Remove temporary audio file only on success
                try:
                    if audio_file.exists(): # Check if it still exists
                        audio_file.unlink()
                        print(f"[Whisper] Removed temporary audio file: {audio_file}")
                    else:
                        print(f"[Whisper] Temporary audio file already removed or not found: {audio_file}")
                except Exception as e:
                    # Log failure to remove, but don't let it stop the worker
                    print(f"[Whisper] Warning: Could not remove temporary audio file {audio_file}: {e}", file=sys.stderr)
            else:
                # Optionally keep the audio file for debugging on error
                if audio_file.exists():
                    print(f"[Whisper] Keeping temporary audio file due to failure: {audio_file}", file=sys.stderr)

            # --- Mark Job Done ---
            # Crucial: Mark the job as done in the queue regardless of outcome.
            # This allows queue.join() to eventually unblock if used elsewhere.
            whisper_queue.task_done()
            print(f"--- [Whisper] Finished processing job for: {video_file} ---")
            


def transcribe_videos(
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
    whisper_queue = queue.Queue()
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
    return


# def run_batch_transcribe(
#     input_folder: str | Path,
#     whisper_root: str | Path,
#     prompt: str = "",
#     suffix: tuple[str, ...] = (".m4v", ".mp4", ".mkv"),
#     language: str = "auto"
# ) -> None:
#     """Main loop prompting for input folders and processing videos."""
#     global whisper_queue
#     whisper_queue = queue.Queue()
#     while True:
#         transcribe_videos(input_folder, whisper_root, prompt, suffix,language=language)


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
        transcribe_videos(input_folder, whisper_root, prompt="", suffix=(".m4v",))
