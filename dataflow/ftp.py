import os
import sys
import warnings
import ftputil
import ftplib
from time import sleep
warnings.filterwarnings("ignore",category=DeprecationWarning)

def connect_to_ftp(ip, username, passwd):
    # unused class for later if want to use different ports
    class MySession(ftplib.FTP):
        def __init__(self, host, userid, password, port):
            """Act like ftplib.FTP's constructor but connect to another port."""
            ftplib.FTP.__init__(self)
            self.connect(host, port)
            self.login(userid, password)

    #Connect to ftp host
    ftp_host = ftputil.FTPHost(ip, username, passwd)
    sleep(1)
    print('Connected to ftp_host {}'.format(ip))
    print('Found directories: {}'.format(ftp_host.listdir('')))
    return ftp_host

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
                copy_recursive_ftp(ftp_host, source_path, target_path, ip, username, passwd)
            except FileExistsError:
                print('Directory already exists  {}'.format(target_path))

        # If the item is a file
        else:
            if os.path.isfile(target_path):
                print('File already exists. Skipping.  {}'.format(target_path))
            else:
                print('Transfering file {}'.format(target_path))
                ftp_host.download(source_path, target_path)

def check_for_flag(ftp_host, user, flag):

    batch_found_files = "C:/Users/User/projects/dataflow/scripts/batch_communicate/found_files.txt" # For batch communication

    # Assume did not find files (unless is set to True below)
    with open(batch_found_files, 'w') as file:
        file.write('False')

    flagged_folders = []
    for folder in ftp_host.listdir(user):
        if flag in folder:
            # tell batch we found files
            with open(batch_found_files, 'w') as file:
                file.write('True')
            print('Found flagged directory: {}'.format(folder))
            return folder
    return None

def define_target(target, folder, flag):
    batch_folder_path = "C:/Users/User/projects/dataflow/scripts/batch_communicate/folder_name.txt" # For batch communication
    folder_flagless = folder.replace(flag, '')
    target = os.path.join(target, folder_flagless)
    abort_copy = False

    try:
        os.mkdir(target)
        # tell batch what the folder path is (ripping utility needs this)
        with open(batch_folder_path, 'w') as file:
            file.write(target)
    except FileExistsError:
        print('WARNING: Directory already exists  {}'.format(target))
        print('Aborting copy.')
        abort_copy = True



    return target, abort_copy