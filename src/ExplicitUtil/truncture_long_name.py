# rename_videos.py
import os
from pathlib import Path

# --- Configuration ---
# 1. Set the directory where your video files are located.
#    - Use '.' for the current directory where the script is run.
#    - Use an absolute path for a specific directory, e.g., 'F:\\Movies' on Windows
#      or '/usbdock/videos' on Linux.
TARGET_DIRECTORY = '"F:\DATA\Ts\面具男"'

# 2. Set the maximum length for the filename's base (the part before .m4v).
MAX_FILENAME_LENGTH = 100

# 3. Set the video extension to look for.
VIDEO_EXTENSION = '.m4v'
# --- End of Configuration ---


def truncate_and_generate_nfo():
    """
    Scans the target directory, truncates long .m4v filenames,
    and creates .nfo files with the original name as the title.
    """
    # Convert the configured directory string into a Path object
    target_path = Path(TARGET_DIRECTORY)

    # Verify that the target directory exists
    if not target_path.is_dir():
        print(f"❌ Error: Directory not found at '{TARGET_DIRECTORY}'")
        return

    print(f"📁 Scanning '{target_path.resolve()}' for {VIDEO_EXTENSION} files...")

    # Iterate over every item in the target directory
    for original_video_path in target_path.iterdir():
        
        # Process only files with the specified extension
        if original_video_path.is_file() and original_video_path.suffix.lower() == VIDEO_EXTENSION:
            
            original_basename = original_video_path.stem  # Filename without extension
            
            # Check if the filename's base is longer than the allowed max length
            if len(original_basename) > MAX_FILENAME_LENGTH:
                
                print(f"\nProcessing long filename: '{original_video_path.name}'")

                # --- 1. Prepare New Filenames ---
                # Truncate the basename to the max allowed length
                truncated_basename = original_basename[:MAX_FILENAME_LENGTH]
                
                # Construct the full paths for the new video and NFO files
                new_video_path = original_video_path.with_name(f"{truncated_basename}{VIDEO_EXTENSION}")
                new_nfo_path = original_video_path.with_name(f"{truncated_basename}.nfo")

                # --- 2. Safety Checks ---
                # Check if a file with the new truncated name already exists
                if new_video_path.exists():
                    print(f"  ❗️ SKIPPING: A file named '{new_video_path.name}' already exists.")
                    continue
                # Check if an NFO file for the new name already exists
                if new_nfo_path.exists():
                    print(f"  ❗️ SKIPPING: An NFO file named '{new_nfo_path.name}' already exists.")
                    continue

                # --- 3. Create the .nfo File ---
                # NFO content uses a simple XML format compatible with media centers like Kodi
                nfo_content = f"<movie>\n  <title>{original_basename}</title>\n</movie>"
                
                try:
                    # Write the content to the .nfo file, using UTF-8 for character support
                    new_nfo_path.write_text(nfo_content, encoding='utf-8')
                    print(f"  ✅ Created NFO: '{new_nfo_path.name}'")
                except IOError as e:
                    print(f"  ❌ ERROR: Could not write NFO file. {e}")
                    continue # Skip renaming if the NFO file fails to create

                # --- 4. Rename the Video File ---
                try:
                    original_video_path.rename(new_video_path)
                    print(f"  ➡️  Renamed video to: '{new_video_path.name}'")
                except OSError as e:
                    print(f"  ❌ ERROR: Could not rename video file. {e}")
                    # If renaming fails, remove the NFO file we just created to keep things clean
                    new_nfo_path.unlink()
                    print(f"  🗑️  Cleaned up orphaned NFO file.")
            
            else:
                # This block is for files that are already short enough
                pass # You can add a print statement here if you want to see which files are skipped

    print("\n✨ Scan complete.")


# This makes the script runnable from the command line
if __name__ == "__main__":
    truncate_and_generate_nfo()