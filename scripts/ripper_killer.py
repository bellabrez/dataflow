import os
import sys
from time import sleep

def main(directory):
    raws_exist = True
    while raws_exist:
        sleep(5)
        raws_exist = check_for_raw_files(directory)

    # Kill bruker converter now that no more raws exist
    os.system("ripper_killer.bat")

def check_for_raw_files(directory):
    print('Checking for raw files in directory {}'.format(directory)) 
    for item in os.listdir(directory):
        new_path = directory + '/' + item

        # Check if item is a directory
        if os.path.isdir(new_path):
            raws_exist = check_for_raw_files(new_path)
            
        # If the item is a file
        else:
            if '_RAWDATA_' in item:
                print('Found raw file {}'.format(item))
                return True
    return False

if __name__ == "__main__":
    main(sys.argv[1])