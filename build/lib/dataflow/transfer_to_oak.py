import os
import sys
from shutil import copyfile

def transfer_to_oak(source, target): 
    for item in os.listdir(source):
        # Create full path to item
        source_path = source + '/' + item
        target_path = target + '/' + item

        # Check if item is a directory
        if os.path.isdir(source_path):
            # Create same directory in target
            try:
                os.mkdir(target_path)
                print('Creating directory {}'.format(os.path.split(target_path)[-1]))
                # RECURSE!
                transfer_to_oak(source_path, target_path)
            except FileExistsError:
                print('WARNING: Directory already exists  {}'.format(target_path))
                print('Skipping Directory.')
            
        # If the item is a file
        else:
            if os.path.isfile(target_path):
                print('File already exists. Skipping.  {}'.format(target_path))
            elif source_path[-4:] == '.nii':
                print('Transfering file {}'.format(target_path))
                copyfile(source_path, target_path)
            else:
                pass

def main(args):
    directory_from = args[0]
    directory_to = 'X:/data/Brezovec/2P_Imaging/IMPORTS' + os.path.split(directory_from)[-1]
    try:
        os.mkdir(directory_to)
        print('Moving from  {}'.format(directory_from))
        print('Moving to  {}'.format(directory_to))
        transfer_to_oak(directory_from, directory_to)
        print('Copy completed.')
    except FileExistsError:
        print('WARNING: Directory already exists  {}'.format(directory_to))
        print('Skipping directory.')

if __name__ == "__main__":
    main(sys.argv[1:])