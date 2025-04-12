
import hashlib


def get_hash(file_path):
    """
    Get the SHA-512 hash of a file.
    :param file_path: str
        Path to the file.
    :return: str
        SHA-512 hash of the file.
    """
    sha512 = hashlib.sha512()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha512.update(chunk)
    return sha512.hexdigest()


def compare_video_files(video_list):
    """
    Compare two video files to check if they are the same.
    :param file1: str
        Path to the first video file.
    :param file2: str
        Path to the second video file.
    :return: bool
        True if the files are the same, False otherwise.
    """
    video_hashes = [get_hash(video) for video in video_list]
    are_videos_the_same = len(set(video_hashes)) == 1
    return are_videos_the_same
