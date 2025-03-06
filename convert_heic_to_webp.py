import os
import subprocess
from pathlib import Path
from PIL import Image
import threading
from tqdm import tqdm

def convert_single_heic(heic_path, failed_count, timeout=10, progress_bar=None):
    """Converts a single HEIC file to WebP with a timeout."""
    webp_path = heic_path.with_suffix(".webp")

    try:
        process = subprocess.Popen(
            ["magick", str(heic_path), str(webp_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            process.communicate(timeout=timeout)  # Wait with timeout
        except subprocess.TimeoutExpired:
            process.kill() #Kill the process if timeout occurs.
            print(f"Timeout converting {heic_path}")
            with failed_count["lock"]:
                failed_count["count"] += 1
            if progress_bar:
                progress_bar.update(1)
            return

        # if process.returncode != 0:
                #     print(f"Magick returned non-zero exit code for {heic_path}")
                #     with failed_count["lock"]:
                #         failed_count["count"] += 1
                #     return


        try:
            img = Image.open(webp_path)
            img.close()
        except (FileNotFoundError, OSError, Exception) as e:
            print(f"WebP validation failed: {e}")
            webp_path.unlink(missing_ok=True)
            with failed_count["lock"]:
                failed_count["count"] += 1
            if progress_bar:
                progress_bar.update(1)
            return

        heic_path.unlink()
        # tqdm.write(f"Converted and deleted: {heic_path}",end="\r")

    except FileNotFoundError:
        # print("File not found. Please ensure it's in the folder.")
        return
    except Exception as e:
        tqdm.write(f"An unexpected error occurred during processing {heic_path}: {e}")
        with failed_count["lock"]:
            failed_count["count"] += 1
    finally:
        if progress_bar:
            progress_bar.update(1)

def convert_heic_to_webp_multithreaded(folder_path, num_threads=4, timeout=10):
    """
    Converts HEIC files to WebP using ImageMagick with multithreading, and counts failures.
    """
    folder = Path(folder_path)
    heic_files = list(folder.rglob("*.heic"))+list(folder.rglob("*.HEIC"))+list(folder.rglob("*.jpg"))+list(folder.rglob("*.JPEG"))+list(folder.rglob("*.JPG"))+list(folder.rglob("*.jpeg"))

    failed_count = {"count": 0, "lock": threading.Lock()}

    threads = []
    with tqdm(total=len(heic_files), desc="Converting HEIC to WebP", position=0, leave=True) as progress_bar:
        # for heic_path in heic_files:
        for heic_path in heic_files:
            thread = threading.Thread(target=convert_single_heic, args=(heic_path, failed_count, timeout, progress_bar)) #pass the timeout to the single heic function.
            threads.append(thread)
            thread.start()
            progress_bar.set_postfix_str(heic_path.name)

            if len(threads) >= num_threads:
                for t in threads:
                    t.join()
                threads = []
        progress_bar.update()
        for t in threads:
            t.join()

    tqdm.write(f"Conversion completed. Failed conversions: {failed_count['count']}")

if __name__ == "__main__":
    folder_path = input("Enter the folder path to convert HEIC files: ")
    num_threads = int(input("Enter the number of threads to use: "))
    timeout = int(input("Enter the timeout in seconds: "))
    convert_heic_to_webp_multithreaded(folder_path, num_threads, timeout)
# This code is a Python script that converts HEIC files to WebP format using ImageMagick in a multithreaded manner.