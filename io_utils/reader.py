def chunk_reader(file_name, chunk_size, chunk_queue):

    try:
        with open(file_name, "rb") as f:
            chunk_id = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                # print(chunk)
                chunk_queue.put((chunk_id, chunk))
                chunk_id += 1

        chunk_queue.put(None)
    except FileNotFoundError:
       print('File not found')
    except Exception as e:
        print('Unexpected error: {}'.format(e))
