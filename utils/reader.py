import os, mmap, logging

log = logging.getLogger(__name__)


def read_header(file_path):
    """
    Reads header from file
    :param file_path: path to file
    :return: Header (8B nonce + 4B chunk size) 12B or None
    """
    try:
        with open(file_path, 'rb') as f:
            base_nonce_bytes = f.read(8)
            chunk_size = f.read(4)

            return base_nonce_bytes, chunk_size
    except (FileNotFoundError, PermissionError, IsADirectoryError, OSError) as e:
        log.error(f'Error reading header of: {file_path} - {e}', exc_info=True)
    except Exception as e:
        log.critical(f'Unexpected error reading header: {e}', exc_info=True)


def map_read_file(file_path):
    """
    Creates memory map
    :param file_path: input file path
    :return: reader and memory map obj
    """
    f = None
    try:
        f = open(file_path, 'rb')
        memory_map = mmap.mmap(f.fileno(), 0, tagname=None, access=mmap.ACCESS_READ)
        return f, memory_map
    except (FileNotFoundError, PermissionError, IsADirectoryError, OSError, ValueError) as e:
        log.error(f'Can not open or map: {file_path} - {e}', exc_info=True)
        if f: f.close()
    except Exception as e:
        log.critical(f'Unexpected error setting up mmap: {e}', exc_info=True)
        if f: f.close()


def get_file_size(file_path):
    """
    Gets size of a file
    :param file_path: path of the file
    :return: size
    """
    try:
        with open(file_path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            return file_size
    except (PermissionError, FileNotFoundError, IsADirectoryError, OSError) as e:
        log.error(f'Error opening file: {file_path} - {e}', exc_info=True)
    except Exception as e:
        log.critical(f'Unexpected error getting file size : {e}', exc_info=True)

def does_file_exists(file_path):
    """
    Util function to check if file exists
    :param file_path: path to check
    :return: True if exists else False
    """
    return os.path.exists(file_path)
