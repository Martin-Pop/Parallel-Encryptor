import unittest
from unittest.mock import patch
import os

from multiprocessing import Queue
from utils.crypto import derive_key_from_string

class TestLogic(unittest.TestCase):

    def test_overwrite_input_file(self):

        content = b"Hello World"
        filename = "test_data.txt"
        with open(filename, "wb") as f:
            f.write(content)

        import main as app

        app.in_file_path = filename
        app.out_file_path = filename
        app.is_encryption = True
        app.chunk_size = 1024
        app.nonce = 12345
        app.worker_count = 1

        app.log_queue = Queue()
        app.key = derive_key_from_string('test')

        try:
             app.main() #will err at undefined log variable - ignore
        except Exception:
            pass

        with open(filename, "rb") as f:
            new_content = f.read()

        # input file musnt get overwritten
        self.assertEqual(content, new_content, "Input file was overwritten by output file")

    def test_cleanup_on_crash(self):
        import main as app
        import os

        app.in_file_path = "in.txt"
        app.out_file_path = "out.enc"
        app.is_encryption = True
        app.chunk_size = 1024
        app.nonce = 12345
        app.worker_count = 2

        with open(app.in_file_path, "wb") as f:
            f.write(b"data")

        # mock start_workers to err
        with patch('main.start_workers') as mock_workers:
            mock_workers.side_effect = RuntimeError("Simulated error")

            try:
                app.main()
            except Exception:
                pass

        #if encryption fails there should not be out file
        self.assertFalse(os.path.exists(app.out_file_path),"corrupted file was not removed")

if __name__ == '__main__':
    unittest.main()