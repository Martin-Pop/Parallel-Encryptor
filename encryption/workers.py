from dataclasses import dataclass
from multiprocessing import Queue
from typing import Optional
import logging

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from utils.reader import map_read_file
from utils.writer import map_write_file
from logger.configure import add_queue_handler_to_root

log = logging.getLogger(__name__)

@dataclass(frozen=True)
class EncryptionWorkerConfig:
    log_queue: Queue
    task_queue: Queue
    in_file: str
    out_file: str
    chunk_size: int
    key: bytes
    base_nonce: int
    is_encryption: bool
    stop_token: Optional[object] = None

def encryption_worker(config):
    """
    Encryption worker that runs in process
    :param config: worker configuration
    """

    add_queue_handler_to_root(config.log_queue)

    file_in, mm_in = map_read_file(config.in_file)
    file_out, mm_out = map_write_file(config.out_file)

    aes = AESGCM(config.key)
    cipher_function = aes.encrypt if config.is_encryption else aes.decrypt

    if config.is_encryption:
        input_header_size = 0
        input_step = config.chunk_size

        output_header_size = 12
        output_step = config.chunk_size + 16
    else:
        input_header_size = 12
        input_step = config.chunk_size + 16

        output_header_size = 0
        output_step = config.chunk_size

    try:
        while True:
            task = config.task_queue.get()
            if task == config.stop_token:
                break

            read_offset, chunk_length = task
            chunk_id = (read_offset - input_header_size) // input_step
            chunk_data = mm_in[read_offset: read_offset + chunk_length]

            nonce_int = (config.base_nonce << 32) | chunk_id
            nonce = nonce_int.to_bytes(12, 'big')

            out_data = cipher_function(nonce, chunk_data, None)

            write_offset = output_header_size + (chunk_id * output_step)
            out_len = len(out_data)
            mm_out[write_offset: write_offset + out_len] = out_data
    except InvalidTag:
        log.error(('Encryption' if config.is_encryption else 'Decryption') + 'failed because of invalid key or invalid/corrupted file')
    except Exception as e:
        log.error('Unexpected error has occurred while ' + ('encrypting ' if config.is_encryption else 'decrypting ') + str(e), exc_info=True)
    finally:
        mm_in.close()
        mm_out.close()
        file_in.close()
        file_out.close()
