import os, time, logging

from console.args import parse_args
from utils.crypto import derive_key_from_string

from io_utils.reader import read_header, get_file_size
from io_utils.writer import create_file

from encryption.chunker import create_chunk_task_queue
from encryption.worker_handler import start_workers
from encryption.workers import EncryptionWorkerConfig

from logger.configure import configure_logger_queue, add_queue_handler_to_root


def main():
    # header: 8b - nonce, 4b - chunk size
    start = time.perf_counter()

    file_size_in = get_file_size(in_file_path)
    if not file_size_in: return
    create_file(
        out_file_path,
        file_size_in,
        chunk_size,
        is_encryption,
        nonce.to_bytes(8, 'big') + chunk_size.to_bytes(4, 'big')
    )

    task_queue = create_chunk_task_queue(chunk_size, file_size_in, is_encryption)

    for i in range(worker_count):
        task_queue.put(None)

    worker_configuration = EncryptionWorkerConfig(
        log_queue=log_queue,
        task_queue=task_queue,
        in_file=in_file_path,
        out_file=out_file_path,
        chunk_size=chunk_size,
        key=key,
        base_nonce=nonce,
        is_encryption=is_encryption,
        stop_token=None,
    )

    workers = start_workers(worker_count, worker_configuration)
    for w in workers:
        w.join()

    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000
    log.info(f"PROGRAM FINISHED IN: {elapsed_ms:.3f} ms")


if __name__ == "__main__":

    log = logging.getLogger(__name__)
    log_listener = None
    try:
        # log
        log_queue, log_listener = configure_logger_queue('app.log')
        add_queue_handler_to_root(log_queue)

        log_listener.start()

        # args
        args = parse_args()
        is_encryption = args.encrypt
        in_file_path = args.input
        out_file_path = args.output
        chunk_size = args.chunk_size
        worker_count = args.workers
        key = derive_key_from_string(args.key)

        if is_encryption:
            nonce = int.from_bytes(os.urandom(8), "big")
            chunk_size = args.chunk_size
        else:
            header = read_header(in_file_path)
            nonce = int.from_bytes(header[0], "big")
            chunk_size = int.from_bytes(header[1], "big")

        log.info(f'MODE: {'ENCRYPT' if is_encryption else 'DECRYPT'}')
        log.info(f'IN: {in_file_path}')
        log.info(f'OUT: {out_file_path}')
        log.info(f'CHUNK SIZE: {chunk_size}')
        log.info(f'WORKERS: {worker_count}')
        log.info(f'KEY: {args.key}')

        main()

    except BaseException as e:
        log.critical(f'Unexpected Error has occurred - {e}', exc_info=True)
    finally:
        if log_listener:
            log_listener.stop()
