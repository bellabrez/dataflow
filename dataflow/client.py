import socket
import tqdm
import os
import sleep

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096 # send 4096 bytes each time step

# the ip address or hostname of the server, the receiver
#host = "192.168.1.101"
host = "10.30.115.186" # Luke's laptop
host = "171.65.17.84" # Desktop
# the port, let's use 5001
port = 5001
# the name of file we want to send, make sure it exists
#filename = "data.csv"
#filename = "G:/ftp_imports/20200613/fly1/func_0/SingleImage-06132020-1058-001/SingleImage-06132020-1058-001_Cycle00001_Ch1_000001.ome.tif"
#filename = "G:/luke/20200725__flag__/fly1/func_0/TSeries-12172018-1322-002/CYCLE_000001_RAWDATA_000001"

# create the client socket
s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")


source_directory = "G:/luke/20200725__flag__"

# Make basefolder 
target_directory = '/'.join(source_directory.split('/')[-2:]) # user/folder. will be sent to server
command = "mkdir"
print(F"First sending: {command}{SEPARATOR}{target_directory}")
s.sendall(f"{command}{SEPARATOR}{target_directory}".encode())
sleep.sleep(1)

def socket_recursive_copy(source, target):
    for item in os.listdir(source):
        # Create full path to item

        source_path = source + '/' + item
        target_path = target + '/' + item
        print(source_path)
        # Check if item is a directory
        if os.path.isdir(source_path):
            #print("is dir: {}".format(source_path))
            # Create same directory in target
            command = "mkdir"
            s.sendall(f"{command}{SEPARATOR}{target_path}".encode())
            sleep.sleep(1)
            socket_recursive_copy(source_path, target_path)

        # If the item is a file
        if os.path.isfile(source_path):
            #print("is file: {}".format(source_path))
            command = "cpfile"
            s.sendall(f"{command}{SEPARATOR}{target_path}".encode())
            sleep.sleep(1)
            socket_file_copy(source_path, target_path)

        else:
            print("error")

def socket_file_copy(source_path, target_path):
    filename = os.path.basename(source_path) # for printing purposes only

    # get and send the file size
    filesize = os.path.getsize(source_path)
    command = None
    s.sendall(f"{command}{SEPARATOR}{filesize}".encode())

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(source_path, "rb") as f:
        for _ in progress:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

socket_recursive_copy(source_directory, target_directory)

# close the socket
s.close()