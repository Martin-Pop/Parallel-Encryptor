from multiprocessing import Queue


def create_chunk_task_queue(base_chunk_size, file_size, is_encryption):
    """
    Creates task queue - offsets for reading
    :param base_chunk_size: chunk size
    :param file_size: size of the whole file
    :param is_encryption: encrytption flag
    :return: queue of tasks
    """
    task_queue = Queue()

    if is_encryption:
        current_offset = 0
        read_size = base_chunk_size
    else:
        current_offset = 12
        read_size = base_chunk_size + 16

    while current_offset < file_size:
        bytes_left = file_size - current_offset
        actual_length = min(read_size, bytes_left)

        if actual_length <= 0:
            break

        task_queue.put((current_offset, actual_length))
        current_offset += read_size

    return task_queue
