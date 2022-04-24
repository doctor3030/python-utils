import os
from typing import Optional, List


def get_list_of_files(path: str, ext: Optional[str] = None):
    """
    Finds all files in a given dir and in sub-dirs.

    :param path: root path to search
    :param ext: file extension
    :return: list of files (full path)
    """
    if os.path.isfile(path):
        return [path]
    paths = os.listdir(path)
    all_files: List[str] = []
    # Iterate over all the entries
    for entry in paths:
        # Create full path
        full_path = os.path.join(path, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(full_path):
            all_files += get_list_of_files(full_path, ext)
        else:
            if ext:
                if entry.endswith('.' + ext):
                    all_files.append(full_path)
            else:
                all_files.append(full_path)
    return all_files
