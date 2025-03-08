import subprocess
from pathlib import Path
from PIL import Image
import threading
from tqdm import tqdm


def convert_single_pic(
    pic_path: Path, failed_count: dict, timeout: int = 10, progress_bar:tqdm|None = None
) -> None:
    """Converts a single pic file to WebP with a timeout.
    Args:
        pic_path (Path): Path to the picture file.
        failed_count (dict): Dictionary to count failed conversions.
        timeout (int): Timeout in seconds"""
    webp_path = pic_path.with_suffix(".webp")

    try:
        process = subprocess.Popen(
            ["magick", str(pic_path), "-quality", "80", str(webp_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            process.communicate(timeout=timeout)  # Wait with timeout
        except subprocess.TimeoutExpired:
            process.kill()  # Kill the process if timeout occurs.
            print(f"Timeout converting {pic_path}")
            with failed_count["lock"]:
                failed_count["count"] += 1
            if progress_bar:
                progress_bar.update(1)
            return

        # if process.returncode != 0:
        #     print(f"Magick returned non-zero exit code for {pic_path}")
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

        pic_path.unlink()
        # tqdm.write(f"Converted and deleted: {pic_path}",end="\r")

    except FileNotFoundError:
        # print("File not found. Please ensure it's in the folder.")
        return
    except Exception as e:
        tqdm.write(f"An unexpected error occurred during processing {pic_path}: {e}")
        with failed_count["lock"]:
            failed_count["count"] += 1
    finally:
        if progress_bar:
            progress_bar.update(1)


def convert_pic_to_webp_multithreaded(
    folder_path: str,
    num_threads: int = 4,
    timeout: int = 10,
    exts: tuple[str, ...] = (".heic", ".jpg", ".jpeg"),
) -> None:
    """
    Converts picture files to WebP using ImageMagick with multithreading, and counts failures.
    Args:
        folder_path (str): Path to the folder containing HEIC files.
        num_threads (int): Number of threads to use.
        timeout (int): Timeout in seconds for each conversion.
        exts (tuple): File extensions to search for.
    """
    folder = Path(folder_path)
    pic_files = []
    for ext in exts:
        # Case-insensitive search
        pic_files.extend(
            list(folder.rglob(f"*{ext}")) + list(folder.rglob(f"*{ext.upper()}"))
        )

    failed_count = {"count": 0, "lock": threading.Lock()}

    threads = []
    with tqdm(
        total=len(pic_files), desc="Converting picture to WebP", position=0, leave=True
    ) as progress_bar:
        # for pic_path in pic_files:
        for pic_path in pic_files:
            thread = threading.Thread(
                target=convert_single_pic,
                args=(pic_path, failed_count, timeout, progress_bar),
            )  # pass the timeout to the single heic function.
            threads.append(thread)
            thread.start()
            progress_bar.set_postfix_str(pic_path.name)

            if len(threads) >= num_threads:
                for t in threads:
                    t.join()
                threads = []
        progress_bar.update()
        for t in threads:
            t.join()

    tqdm.write(f"Conversion completed. Failed conversions: {failed_count['count']}")


if __name__ == "__main__":
    folder_path = input("Enter the folder path to convert picture files: ")
    num_threads = int(input("Enter the number of threads to use: "))
    timeout = int(input("Enter the timeout in seconds: "))
    convert_pic_to_webp_multithreaded(folder_path, num_threads, timeout)
# This code is a Python script that converts picture files to WebP format using ImageMagick in a multithreaded manner.
