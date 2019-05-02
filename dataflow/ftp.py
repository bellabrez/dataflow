import os
import sys
import warnings
import ftputil
import ftplib
import json
import ast
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
def start_copy_recursive_ftp(*args):
    copy_recursive_ftp(*args)

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
                # Check if the user's folder has a dataflow.json file
                if item == 'dataflow.json':
                    metadata_file = user + '/' + item
                    print('Found metadata {}'.format(metadata_file))
                    #Copy the metadata info
                    with ftp_host.open(metadata_file) as fobj:
                        # Read in as string
                        metadata = fobj.read()
                        # Convert to dict
                        metadata = ast.literal_eval(metadata)
            if flagged_folder is not None:
                return flagged_folder, metadata
    raise SystemExit # Exit everything if no flagged folder

def check_for_target(full_target):
    try:
        os.mkdir(full_target)
    except FileExistsError:
        print('WARNING: Directory already exists  {}'.format(full_target))
        print('Aborting.')
        raise SystemExit