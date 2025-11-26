from multiprocessing import Process, Queue
from .workers import encryption_worker, decryption_worker

def start_workers(worker_count, task_queue, key, base_nonce, encrypt ,stop_token=None):
    result_queue = Queue()

    target = encryption_worker if encrypt else decryption_worker

    workers = []
    for _ in range(worker_count):
        process = Process(target=target, args=(task_queue, result_queue, key, base_nonce, stop_token))
        workers.append(process)

        process.start()

    return result_queue, workers

def stop_workers(worker_count, task_queue, stop_token=None):
    for _ in range(worker_count):
        task_queue.put(stop_token)

def terminate_workers(workers):
    for worker in workers:
        worker.terminate()
