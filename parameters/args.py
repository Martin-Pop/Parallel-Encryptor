import argparse, os

from io_utils.reader import read_header
from utils.crypto import derive_key_from_string

class ArgumentParserCustom(argparse.ArgumentParser):
    """
    Argument parser with overwritten error handling to pass the error further (to my logger)
    """
    def error(self, message):
        raise ValueError(message)


def parse_args():
    """
    Parses command line arguments
    :return: namespace of parsed arguments
    """

    parser = ArgumentParserCustom(
        description="Parallel AES-GCM encryptor / decryptor"
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "-e", "--encrypt",
        action="store_true",
        help="Encrypt input file"
    )
    mode_group.add_argument(
        "-d", "--decrypt",
        action="store_true",
        help="Decrypt input file"
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to input file"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Path to output file"
    )

    parser.add_argument(
        "-c", "--chunk-size",
        type=int,
        default=1024 * 1024, #1MB
        help="Chunk size in bytes (default 1MB)"
    )

    parser.add_argument(
        "-k", "--key",
        required=True,
        help="Encryption key"
    )

    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=2,
        help="Number of worker processes (default 2)"
    )

    return parser.parse_args()


def validate_args(args):

    is_encryption = args.encrypt
    in_file_path = args.input
    out_file_path = args.output

    if args.chunk_size <= 0:
        raise ValueError("Chunk size must be a positive integer")

    if args.workers <= 0:
        raise ValueError("Worker count must be a positive integer")

    if not os.path.exists(in_file_path):
        raise ValueError("Input file does not exist")

    key = derive_key_from_string(args.key)

    if is_encryption:
        nonce = int.from_bytes(os.urandom(8), "big")
        chunk_size = args.chunk_size
    else:
        header = read_header(in_file_path)

        if not header:
            raise ValueError("Input file does not contain a header")

        nonce = int.from_bytes(header[0], "big")
        chunk_size = int.from_bytes(header[1], "big")

    return {
        'is_encryption': is_encryption,
        'in_file_path': in_file_path,
        'out_file_path': out_file_path,
        'chunk_size': chunk_size,
        'worker_count': args.workers,
        'key': key,
        'nonce': nonce,
        'key_string': args.key
    }