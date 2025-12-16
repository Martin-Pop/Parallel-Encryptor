# AES-GCM File Encryptor

* **Author:** Martin Pop
*  **Date:** Nov 26 - Dec 16 2025
* **Project Type:** School Project with parallelization

---

> ⚠️ **WARNING**
> * **Do not use this tool to encrypt important or sensitive data without having a backup.**

---

## Overview

This is a Python tool designed for encrypting and decrypting files
using **AES-256-GCM** (Galois/Counter Mode). Uses **multiprocessing** and **memory-mapped files (`mmap`)**.
This allows it to process data chunks in parallel.

---

## Key Features

* **Algorithm:** AES-256-GCM (Authenticated Encryption Standard).
* **Parallel Processing:** Uses a workers to encrypt/decrypt chunks concurrently.
* **Memory Efficiency:** Utilizes `mmap` to handle files larger than available RAM.

---

## Requirements

* Python 3.8+
* Third-Party Libraries:
    * `cryptography` library used for encryption / decryption
* Build tools:
    * `pyinstaller` library for compiling into one executable file

---

## How It Works

* The tool splits the input file into fixed-size chunks to allow parallel processing.
* Encryption: 
    * Reads N bytes of raw data.
    * Writes N + 16 bytes (Encrypted Data + 16-byte Auth Tag).
* Decryption: 
    * Reads N + 16 bytes.
    * Writes N bytes of raw data.
* Encrypted file structure: 
    * Header (12 bytes): 8 bytes for nonce and 4 bytes for chunk size.
    * Encrypted data (n bytes)

---

## Known Issues & Limitations

* Keyboard interrupt while **starting processes** will freeze your console!
* There is no limit for worker count, however high number is not recommended!
---

## Usage

### 1. Installation

* Download latest release
* If you want to compile yourself or run in your python enviroment:
    * clone repo `git clone https://github.com/Martin-Pop/Parallel-Encryptor.git`
    * change directory: `cd Parallel-Encryptor`
    * create virtual enviroment `python -m venv .venv`
    * activate vevn `.\.venv\Scripts\activate`
    * download dependencies `pip install -r requirements.txt`
    * run `python main.py ....` or compile with pyinstaller `pyinstaller main.py`

### 2. Running the Script
The script is run via the command line. You must specify whether you want to encrypt (-e) or decrypt (-d) the file.
```Bash
<entry point> [mode] -i <input_file> -o <output_file> -k <key> [options]
```

| Argument    | Flag              | Required | Description                                                   |
|-------------|-------------------|----------|---------------------------------------------------------------|
| Mode        | -e, --encrypt     | Yes*     | Encrypt the input file.                                      |
| Mode        | -d, --decrypt     | Yes*     | Decrypt the input file.                                      |
| Input       | -i, --input       | Yes      | Path to the source file.                                     |
| Output      | -o, --output      | Yes      | Path to the destination file.                                |
| Key         | -k, --key         | Yes      | The encryption key string. Ensure it is strong!              |
| Chunk Size  | -c, --chunk-size  | No       | Size of data chunks in bytes. Default: 1048576 (1MB).        |
| Workers     | -w, --workers     | No       | Number of parallel worker processes. Default: 2.             |
| Force       | -f, --force       | No       | Forces overwriting existing output file.                     |


---

## Errors

Errors are printed to the console as well as logged into file `app.log` found in the same directory as program entry point 
. Some errors logs also contains traceback.

---

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND
