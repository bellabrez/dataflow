from socket import *
import os

CHUNKSIZE = 1_000_000

# host = 'localhost'
# port = 5000
# source_directory = "/Users/lukebrezovec/Desktop/test"

host = "171.65.17.84"
port = 5001
source_directory = "/Users/lukebrezovec/Desktop/test"

#source_directory = "G:/luke/20200725__flag__"

sock = socket()
sock.connect((host,port))

for path,dirs,files in os.walk(source_directory):
    for file in files:
        filename = os.path.join(path,file)
        relpath = '/'.join(filename.split('/')[1:])
        #relpath = os.path.join(user_folder,file)
        #relpath = os.path.relpath(filename,source_directory)
        filesize = os.path.getsize(filename)

        print(f'Sending {relpath}')

        with open(filename,'rb') as f:
            sock.sendall(relpath.encode() + b'\n')
            sock.sendall(str(filesize).encode() + b'\n')

            # Send the file in chunks so large files can be handled.
            while True:
                data = f.read(CHUNKSIZE)
                if not data: break
                sock.sendall(data)
print('Done.')