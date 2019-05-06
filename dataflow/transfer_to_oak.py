import os
import sys
from shutil import copyfile
from dataflow.utils import timing

def transfer_to_oak(source, target, allowable_extensions): 
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
            except FileExistsError:
                print('WARNING: Directory already exists  {}'.format(target_path))
                print('Skipping Directory.')

            # RECURSE!
            transfer_to_oak(source_path, target_path, allowable_extensions)
        
        # If the item is a file
        else:
            if os.path.isfile(target_path):
                print('File already exists. Skipping.  {}'.format(target_path))
            elif allowable_extensions is None:
                print('Transfering file {}'.format(target_path))
                copyfile(source_path, target_path)
            elif source_path[-4:] in allowable_extensions:
                print('Transfering file {}'.format(target_path))
                copyfile(source_path, target_path)
            else:
                pass

@timing
def start_oak_transfer(directory_from, oak_target, allowable_extensions, add_flag=True):
    directory_to = os.path.join(oak_target, os.path.split(directory_from)[-1])
    try:
        os.mkdir(directory_to)
        print('Moving from  {}'.format(directory_from))
        print('Moving to  {}'.format(directory_to))
        transfer_to_oak(directory_from, directory_to, allowable_extensions)
        print('Copy completed.')
        if add_flag:
            os.rename(directory_to, directory_to + '__done__')
            print('Added __done__ flag')

    except FileExistsError:
        print('WARNING: Directory already exists  {}'.format(directory_to))
        print('Skipping directory.')