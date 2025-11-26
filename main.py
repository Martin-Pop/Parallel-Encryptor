from multiprocessing import Queue, Process

from io_utils.reader import chunk_reader

def main():

    file_path = 'test.txt'
    chunk_size = 1024
    chunk_queue = Queue()

    reader = Process(target= chunk_reader, args=(file_path, chunk_size, chunk_queue))
    reader.start()

    reader.join()
    print('Done')
    print(chunk_queue)


if __name__ == "__main__":
    main()
