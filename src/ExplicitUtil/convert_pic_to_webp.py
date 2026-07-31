import subprocess
from pathlib import Path
from PIL import Image
import threading
from tqdm import tqdm
import platform
import zipfile
import tempfile
import shutil

__docformat__ = "google"
def convert_single_pic(
    pic_path: Path,
    failed_count: dict,
    timeout: int = 10,
    progress_bar: tqdm | None = None,
    quality: int = 80,
) -> None:
    """Converts a single pic file to WebP with a timeout.
    
    Args:
    
        pic_path (Path): Path to the picture file.
        failed_count (dict): Dictionary to count failed conversions.
        timeout (int): Timeout in seconds
        progress_bar (tqdm): Progress bar for tracking progress.
        quality (int): Quality of the WebP image.
    """
    webp_path = pic_path.with_suffix(".webp")

    try:
        if platform.system() == "Linux":
            command = ["convert", str(pic_path), "-quality", str(quality), str(webp_path)]
        else:
            command = [
            "magick",
            str(pic_path),
            "-quality",
            str(quality),
            str(webp_path),
            ]
        process = subprocess.Popen(
            command,
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
    exts: tuple[str, ...] = (".heic", ".jpg", ".jpeg", ".png", ".tiff"),
    quality: int = 80,
) -> None:
    """
    Converts picture files to WebP using ImageMagick with multithreading, and counts failures.
    
    Args:
    
        folder_path (str): Path to the folder containing HEIC files.        
        num_threads (int): Number of threads to use. Default is 4.
        timeout (int): Timeout in seconds for each conversion. Default is 10 seconds.
        exts (tuple): File extensions to search for. Default is (".heic", ".jpg", ".jpeg", ".png", ".tiff").
        quality (int): Quality of the WebP image. Default is 80.
    """
    folder = Path(folder_path)
    # ⚡ Bolt Optimization: Use a single pass to find all matching files.
    # Instead of traversing the entire directory tree 2*N times (once for lower, once for upper per extension),
    # we traverse it once and check if the suffix matches in O(1) time using a set.
    exts_lower = {ext.lower() for ext in exts}
    pic_files = [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in exts_lower]

    failed_count = {"count": 0, "lock": threading.Lock()}

    threads = []
    with tqdm(
        total=len(pic_files), desc="Converting picture to WebP", position=0, leave=True
    ) as progress_bar:
        # for pic_path in pic_files:
        for pic_path in pic_files:
            thread = threading.Thread(
                target=convert_single_pic,
                args=(pic_path, failed_count, timeout, progress_bar, quality),
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


def convert_pics_in_zips(
    folder_path: str,
    num_threads: int = 4,
    timeout: int = 10,
    exts: tuple[str, ...] = (".heic", ".jpg", ".jpeg", ".png", ".tiff"),
    quality: int = 80,
) -> None:
    """
    Finds all zip files in folder_path, extracts images from them,
    converts the images to WebP, and repacks them back into the zip,
    overwriting the original zip file.

    Args:

        folder_path (str): Path to the folder containing zip files.
        num_threads (int): Number of threads to use for conversion.
        timeout (int): Timeout in seconds for each conversion.
        exts (tuple): File extensions to search for inside zips.
        quality (int): Quality of the WebP image.
    """
    folder = Path(folder_path)
    zip_files = list(folder.rglob("*.zip"))

    if not zip_files:
        tqdm.write("No zip files found.")
        return

    exts_lower = {ext.lower() for ext in exts}

    for zip_path in tqdm(zip_files, desc="Processing zip files", position=0, leave=True):
        tqdm.write(f"Processing: {zip_path}")
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)

                # Extract all files from the zip
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(tmp_path)

                # Find image files inside the extracted content
                pic_files = [
                    p for p in tmp_path.rglob("*")
                    if p.is_file() and p.suffix.lower() in exts_lower
                ]

                if not pic_files:
                    tqdm.write(f"  No matching images found in {zip_path.name}, skipping.")
                    continue

                # Convert images to WebP using the existing conversion logic
                failed_count = {"count": 0, "lock": threading.Lock()}
                threads = []

                with tqdm(
                    total=len(pic_files),
                    desc=f"  Converting in {zip_path.name}",
                    position=1,
                    leave=False,
                ) as progress_bar:
                    for pic_path in pic_files:
                        thread = threading.Thread(
                            target=convert_single_pic,
                            args=(pic_path, failed_count, timeout, progress_bar, quality),
                        )
                        threads.append(thread)
                        thread.start()
                        progress_bar.set_postfix_str(pic_path.name)

                        if len(threads) >= num_threads:
                            for t in threads:
                                t.join()
                            threads = []
                    for t in threads:
                        t.join()

                # Repack everything into a new zip, overwriting the original
                new_zip_path = zip_path.with_suffix(".tmpzip")
                with zipfile.ZipFile(new_zip_path, "w", zipfile.ZIP_DEFLATED) as zf_out:
                    for f in sorted(tmp_path.rglob("*")):
                        if f.is_file():
                            arcname = f.relative_to(tmp_path)
                            zf_out.write(f, arcname)

                # Replace the old zip with the new one
                new_zip_path.replace(zip_path)

                tqdm.write(
                    f"  Done: {zip_path.name} — {len(pic_files)} converted, "
                    f"{failed_count['count']} failed."
                )

        except Exception as e:
            tqdm.write(f"  Error processing {zip_path}: {e}")


if __name__ == "__main__":
    folder_path = input("Enter the folder path to convert picture files: ").strip('"')
    num_threads = int(input("Enter the number of threads to use: "))
    timeout = int(input("Enter the timeout in seconds: "))
    convert_pic_to_webp_multithreaded(folder_path, num_threads, timeout)

