import socket
import tqdm
import os
# device's IP address
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# create the server socket
# TCP socket
s = socket.socket()

# bind the socket to our local address
s.bind((SERVER_HOST, SERVER_PORT))

# enabling our server to accept connections
# 5 here is the number of unaccepted connections that
# the system will allow before refusing new connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

# accept connection if there is any
client_socket, address = s.accept() 
# if below code is executed, that means the sender is connected
print(f"[+] {address} is connected.")

master_directory = "G:/ftp_imports"

def socket_file_copy(item_path, filesize):
    filename = os.path.basename(item_path) # for printing purposes only

    # convert to integer
    filesize = int(filesize)

    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(item_path, "wb") as f:
        for _ in progress:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)

            try:
                # this split operation will fail if there is no separator
                # which means the file is still being copied, so the exception clause will be entered
                _, _ = bytes_read.decode().split(SEPARATOR)
                break
            except:    
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

#todo: create user's folder in ftp_imports if first time running
while True:
    message = client_socket.recv(BUFFER_SIZE)
    print("message: {}".format(message))
    command, item = message.decode().split(SEPARATOR)
    item_path = os.path.join(master_directory, item)

    if command == "mkdir":
        os.mkdir(item_path)
        print("making directory: {}".format(item_path))
    if command == "cpfile":
        #get filesize
        command, filesize = client_socket.recv(BUFFER_SIZE).decode().split(SEPARATOR)
        socket_file_copy(item_path, filesize)


# close the client socket
client_socket.close()
# close the server socket
s.close()