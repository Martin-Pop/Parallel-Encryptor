from multiprocessing import Queue, Process
import os

from io_utils.reader import chunk_reader, read_header
from io_utils.writer import chunk_writer
from encryption.worker_handler import start_workers, stop_workers

def main():

    #header: 8b - nonce, 4b - chunk size
    # 1242652385986301932
    # 50

    #TODO: load from args and conf
    is_encryption = False
    in_file_path = 'encryption.txt'
    out_file_path = 'result.txt'
    worker_count = 4
    default_chunk_size = 5
    #Todo do checks
    header = read_header(in_file_path) if not is_encryption else None
    print(header)
    if header is None:
        print('def')
        nonce = int.from_bytes(os.urandom(8), "big")
        chunk_size = default_chunk_size
    else:
        nonce = int.from_bytes(header[0], "big")
        chunk_size = int.from_bytes(header[1], "big")

    key = b'\x1eEeW7\x95>q\xc0\x90\x08\xc8\xb8\xa6\xef\xb1\xd3\n\xa6*6]>\x84\xd4\x17\x85\x01\x7f\xeb\xfc"'  # os.urandom(32)

    print(nonce)
    print(chunk_size)

    task_queue = Queue()

    #read
    reader = Process(
        target= chunk_reader,
        args=(in_file_path, chunk_size, task_queue, is_encryption)
    )
    reader.start()

    #work
    result_queue, workers = start_workers(worker_count, task_queue, key, nonce, is_encryption, None)

    #write
    print(header)
    writer = Process(
        target= chunk_writer,
        args=(out_file_path, result_queue, is_encryption ,nonce.to_bytes(8,'big') + chunk_size.to_bytes(4,'big'), None)
    )
    writer.start()

    #stop
    reader.join()
    stop_workers(worker_count, task_queue)

    result_queue.put(None)
    writer.join()
    print('writer end')

    for worker in workers:
        print('joining worker')
        worker.join()

    print('end')

    # t = read_header(out_file_path)
    # print(t)
    # print(int.from_bytes(t[0], "big"))
    # print(int.from_bytes(t[1], "big"))

if __name__ == "__main__":
    main()
