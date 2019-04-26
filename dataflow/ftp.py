import ftputil
import os

def copy_recursive_ftp(ftp_host, source, target):    
    for item in ftp_host.listdir(source):
        # Create full path to item
        source_path = os.path.join(source,item)
        target_path = os.path.join(target,item)

        # Check if item is a directory
        if ftp_host.path.isdir(source_path):
            # Create same directory in target
            os.mkdir(target_path)
            
            # RECURSE!
            copy_recursive_ftp(ftp_host, source_path, target_path)
            
        # If the item is a file
        else:
            ftp_host.download(source_path, target_path)