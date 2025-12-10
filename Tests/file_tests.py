import unittest, os, mmap
from unittest.mock import patch

from multiprocessing import Queue
from utils.crypto import derive_key_from_string

import main as app

class FileTest(unittest.TestCase):

    def test_overwrite_input_file(self):

        content = b"Hello World"
        filename = "test_data.txt"
        with open(filename, "wb") as f:
            f.write(content)

        args = {
            'is_encryption': True,
            'in_file_path': filename,
            'out_file_path': filename,
            'chunk_size': 1024,
            'worker_count': 1,
            'key': derive_key_from_string('test'),
            'nonce': 12345,
            'key_string': 'test'
        }

        app.validated_args = args
        app.log_queue = Queue()

        try:
             app.main() #will err at undefined log variable - ignore
        except Exception:
            pass

        with open(filename, "rb") as f:
            new_content = f.read()

        # input file musnt get overwritten
        self.assertEqual(content, new_content, "Input file was overwritten by output file")

    def test_cleanup_on_crash(self):

        in_file = 'in.txt'
        out_file = 'out.bin'

        args = {
            'is_encryption': True,
            'in_file_path': in_file,
            'out_file_path': out_file,
            'chunk_size': 1024,
            'worker_count': 2,
            'key': derive_key_from_string('test'),
            'nonce': 12345,
            'key_string': 'test'
        }

        app.validated_args = args

        with open(in_file, "wb") as f:
            f.write(b"data")

        # mock start_workers to err
        with patch('main.start_workers') as mock_workers:
            mock_workers.side_effect = RuntimeError("Simulated error")

            try:
                app.main()
            except Exception:
                pass

        #if encryption fails there should not be out file
        self.assertFalse(os.path.exists(out_file),"corrupted file was not removed")

if __name__ == '__main__':
    unittest.main()