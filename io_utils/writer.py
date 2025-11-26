def chunk_writer(file_path, result_queue, is_encryption, header, stop_token):
    try:
        with open(file_path, "wb") as f:

            if is_encryption:
                f.write(header)

            next_chunk_id = 0
            buffer = {}

            while True:
                result = result_queue.get()
                if result == stop_token:
                    break

                chunk_id, data = result
                buffer[chunk_id] = data

                while next_chunk_id in buffer:
                    f.write(buffer.pop(next_chunk_id))
                    next_chunk_id += 1

    except FileNotFoundError:
        print('File not found')
    except Exception as e:
        print('W Unexpected error: {}'.format(e))