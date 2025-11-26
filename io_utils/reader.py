def chunk_reader(file_name, chunk_size, chunk_queue, is_encryption):
    try:
        with open(file_name, 'rb') as f:

            if not is_encryption:
                f.seek(12)
                chunk_size += 16

            chunk_id = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                # print(chunk)
                chunk_queue.put((chunk_id, chunk))
                chunk_id += 1

        print('reader end')

    except FileNotFoundError:
       print('File not found')
    except Exception as e:
        print('Unexpected error: {}'.format(e))

def read_header(file_path):
    try:
        with open(file_path, 'rb') as f:
            base_nonce_bytes = f.read(8)
            chunk_size = f.read(4)

            return base_nonce_bytes, chunk_size
    except FileNotFoundError:
        print('File not found')
        return None
    except Exception as e:
        print('Unexpected error: {}'.format(e))
        return None
