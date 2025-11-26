from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encryption_worker(task_queue, result_queue, key, base_nonce, stop_token):

    aes = AESGCM(key)
    while True:
        task = task_queue.get()

        if task == stop_token:
            # print('Task stopped')
            break

        chunk_id, chunk = task

        nonce_int = (base_nonce << 32) | chunk_id
        nonce = nonce_int.to_bytes(12, 'big')

        ciphertext = aes.encrypt(nonce, chunk, None)
        print(len(ciphertext))
        result_queue.put((chunk_id, ciphertext))

def decryption_worker(task_queue, result_queue, key, base_nonce, stop_token):

    aes = AESGCM(key)
    while True:
        task = task_queue.get()

        if task == stop_token:
            break

        chunk_id, chunk = task

        nonce_int = (base_nonce << 32) | chunk_id
        nonce = nonce_int.to_bytes(12, "big")
        plaintext = aes.decrypt(nonce, chunk, None)
        result_queue.put((chunk_id, plaintext))