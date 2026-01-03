import subprocess
import os

def merge_videos(video_files, output_file):
    """
    Merge multiple video files using ffmpeg concat method.

    Args:
        video_files (list of str): List of video file paths to merge.
        output_file (str): Path to the output merged video file.

    Returns:
        None
    """
    # Create a temporary file to list all video files
    with open("file_list.txt", "w") as file_list:
        for video in video_files:
            file_list.write(f"file '{os.path.abspath(video)}'\n")
    
    # Run ffmpeg command to merge videos
    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "file_list.txt",
        "-c", "copy",
        output_file
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Videos merged successfully into {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during merging: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists("file_list.txt"):
            os.remove("file_list.txt")