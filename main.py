import time, logging

from parameters.args import parse_args, validate_args

from io_utils.reader import get_file_size
from io_utils.writer import create_file

from encryption.chunker import create_chunk_task_queue
from encryption.worker_handler import start_workers
from encryption.workers import EncryptionWorkerConfig

from logger.configure import configure_logger_queue, add_queue_handler_to_root


def main():
    # header: 8b - nonce, 4b - chunk size

    start = time.perf_counter()

    file_size_in = get_file_size(validated_args['in_file_path'])
    if not file_size_in:
        return

    # output file
    create_file(
        validated_args['out_file_path'],
        file_size_in,
        validated_args['chunk_size'],
        validated_args['is_encryption'],
        validated_args['nonce'].to_bytes(8, 'big') + validated_args['chunk_size'].to_bytes(4, 'big')  # header
    )

    task_queue = create_chunk_task_queue(validated_args['chunk_size'], file_size_in, validated_args['is_encryption'])

    #put in stop tokens
    for _ in range(validated_args['worker_count']):
        task_queue.put(None)

    worker_configuration = EncryptionWorkerConfig(
        log_queue=log_queue,
        task_queue=task_queue,
        in_file=validated_args['in_file_path'],
        out_file=validated_args['out_file_path'],
        chunk_size=validated_args['chunk_size'],
        key=validated_args['key'],
        base_nonce=validated_args['nonce'],
        is_encryption=validated_args['is_encryption'],
        stop_token=None,
    )

    workers = start_workers(validated_args['worker_count'], worker_configuration)
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
        validated_args = validate_args(args)

        log.info(f'MODE: {'ENCRYPT' if validated_args['is_encryption'] else 'DECRYPT'}')
        log.info(f'IN: {validated_args["in_file_path"]}')
        log.info(f'OUT: {validated_args["out_file_path"]}')
        log.info(f'CHUNK SIZE: {validated_args["chunk_size"]}')
        log.info(f'WORKERS: {validated_args["worker_count"]}')
        log.info(f'KEY: {validated_args["key_string"]}')

        main()
    except ValueError as e:
        log.error(f'Invalid argument value: {e}')
    except BaseException as e:
        log.critical(f'Unexpected Error has occurred - {e}', exc_info=True)
    finally:
        if log_listener:
            log_listener.stop()
