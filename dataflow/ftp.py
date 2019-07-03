import os
import sys
import warnings
import ftputil
import ftplib
import json
import ast
import shutil
from time import sleep
from dataflow.utils import timing
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

@timing
def start_copy_recursive_ftp(*args, **kwargs):
    copy_recursive_ftp(*args, **kwargs)

def copy_recursive_ftp(ftp_host, source, target, ip, username, passwd, skip_existing_directories=False): 
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
                continue
            if not skip_existing_directories:
                copy_recursive_ftp(ftp_host, source_path, target_path, ip, username, passwd)

        # If the item is a file
        else:
            if os.path.isfile(target_path):
                print('File already exists. Skipping. {}'.format(target_path))
            else:
                print('Transfering file {}'.format(target_path))
                ftp_host.download(source_path, target_path)

def check_for_flag(ftp_host, flag):
    # Look in each user folder
    for user in ftp_host.listdir(''):
        metadata = None
        flagged_folder = None
        # Check if an actual directory
        if ftp_host.path.isdir(user):
            # Get all items in this user's directory
            items = ftp_host.listdir(user)
            # Do any items have a flag?
            for item in items:
                if flag in item:
                    flagged_folder = item
                    print('Found flagged directory {} in {}'.format(flagged_folder, user))
                    # Check for dataflow.json file
                    for item in items:
                        if item == 'dataflow.json':
                            metadata_file = user + '/' + item
                            print('Found metadata for user {}'.format(metadata_file))
                            #Copy the metadata info
                            with ftp_host.open(metadata_file) as fobj:
                                # Read in as string
                                metadata = fobj.read()
                                # Convert to dict
                                metadata = ast.literal_eval(metadata)
            if flagged_folder is not None and metadata is not None:
                return flagged_folder, metadata, user
    print('No flagged folders found.')
    raise SystemExit # Exit everything if no flagged folder

def check_for_target(full_target, quit_if_local_target_exists):
    try:
        os.mkdir(full_target)
    except FileExistsError:
        print('WARNING: Directory already exists  {}'.format(full_target))
        if quit_if_local_target_exists:
            print('Aborting.')
            raise SystemExit

def get_dir_size_ftp(ftp_host, directory):
    total_size = 0
    for dirpath, dirnames, filenames in ftp_host.walk(directory):
        for f in filenames:
            fp = dirpath + '/' + f
            total_size += ftp_host.path.getsize(fp)
    return total_size

def get_dir_size_local(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def confirm_bruker_transfer(ip, username, passwd, bruker_folder, full_target):
    destination_size = get_dir_size_local(full_target)
    print('Destination size: {}'.format(destination_size))
    ftp_host = ftputil.FTPHost(ip, username, passwd)
    source_size = get_dir_size_ftp(ftp_host, bruker_folder)
    print('Bruker size: {}'.format(source_size))
    if source_size !=0 and destination_size !=0 and source_size == destination_size:
        print('Source and desitination directory sizes match.')
    else:
        print('Source and desitination directory sizes DO NOT match.')
        raise SystemExit

def delete_bruker_folder(ip, username, passwd, bruker_folder):
    ftp_host = ftputil.FTPHost(ip, username, passwd)
    ftp_host.rmtree(bruker_folder)
    print('DELETED: {}'.format(bruker_folder))

def strip_bruker_flag(ip, username, passwd, bruker_folder, flag):
    ftp_host = ftputil.FTPHost(ip, username, passwd)
    flagless_folder = bruker_folder.replace(flag, '')
    ftp_host.rename(bruker_folder, flagless_folder)
    print('Renamed bruker folder to {}'.format(flagless_folder))

def delete_local(directory):
    shutil.rmtree(directory)
    print('DELETED: {}'.format(directory))