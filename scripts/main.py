### Every minute:

import sys
import os
import warnings
import ftputil
import ftplib
from time import sleep
from dataflow import copy_recursive_ftp

warnings.filterwarnings("ignore",category=DeprecationWarning)

def copy_recursive_ftp(ftp_host, source, target, ip, username, passwd): 
    for item in ftp_host.listdir(source):
        ftp_host = ftputil.FTPHost(ip, username, passwd)

        # Create full path to item
        source_path = source + '/' + item
        target_path = target + '/' + item

        # Check if item is a directory
        if ftp_host.path.isdir(source_path):
            # Create same directory in target
            try:
                os.mkdir(target_path)
            except FileExistsError:
                print('Directory already exists  {}'.format(target_path))

            # RECURSE!
            copy_recursive_ftp(ftp_host, source_path, target_path, ip, username, passwd)
            
        # If the item is a file
        else:
            if os.path.isfile(target_path):
                print('File already exists. Skipping.  {}'.format(target_path))
            else:
                print('Transfering file {}'.format(target_path))
                ftp_host.download(source_path, target_path)

class MySession(ftplib.FTP):
    def __init__(self, host, userid, password, port):
        """Act like ftplib.FTP's constructor but connect to another port."""
        ftplib.FTP.__init__(self)
        self.connect(host, port)
        self.login(userid, password)

ip = '171.65.18.54'
username = 'user'
passwd = 'flyeye'
target = 'F:/FTP_IMPORTS'
batch_found_files = "C:/Users/User/projects/dataflow/scripts/found_files.txt"
batch_folder_path = "C:/Users/User/projects/dataflow/scripts/folder_name.txt"
ftp_host = ftputil.FTPHost(ip, username, passwd, port=21, session_factory=MySession)

#Connect to ftp host
#ftp_host = ftputil.FTPHost(ip, username, passwd)
sleep(1)
print('Connected to ftp_host {}'.format(ip))
print('Found directories: {}'.format(ftp_host.listdir('')))

# Assume did not find files (unless is set to True below)
with open(batch_found_files, 'w') as file:
    file.write('False')

for folder in ftp_host.listdir(''):
    if '__flag__' in folder:
        # tell batch we found files
        with open(batch_found_files, 'w') as file:
            file.write('True')

        print('Found flagged directory: {}'.format(folder))
        print('Start Copy')
        target = target + '/' + folder

        # tell batch what the folder path is (ripping utility needs this)
        with open(batch_folder_path, 'w') as file:
            file.write(target)

        try:
            os.mkdir(target)
            copy_recursive_ftp(ftp_host, folder, target, ip, username, passwd)
            print('Copy completed.')
        except FileExistsError:
            print('WARNING: Directory already exists  {}'.format(target))
            print('Skipping directory.')

        