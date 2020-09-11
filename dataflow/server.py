from socket import *
import os

CHUNKSIZE = 1_000_000
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
target_directory = "G:/ftp_imports"

# SERVER_HOST = ""
# SERVER_PORT = 5000
# target_directory = "/Users/lukebrezovec/projects/dataflow/dataflow/target"

sock = socket()
sock.bind((SERVER_HOST, SERVER_PORT))
sock.listen(1)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

# Make a directory for the received files.
#os.makedirs('server',exist_ok=True)

client,address = sock.accept()
print(f"[+] {address} is connected.")
with client,client.makefile('rb') as clientfile:
    while True:
        raw = clientfile.readline()
        if not raw: break # no more files, server closed connection.

        filename = raw.strip().decode()
        length = int(clientfile.readline())
        print(f'Downloading {filename}...\n  Expecting {length:,} bytes...',end='',flush=True)

        path = os.path.join(target_directory,filename)
        os.makedirs(os.path.dirname(path),exist_ok=True)

        # Read the data in chunks so it can handle large files.
        with open(path,'wb') as f:
            while length:
                chunk = min(length,CHUNKSIZE)
                data = clientfile.read(chunk)
                if not data: break
                f.write(data)
                length -= len(data)
            else: # only runs if while doesn't break and length==0
                print('Complete')
                continue

# close the client socket
client.close()
# close the server socket
sock.close()