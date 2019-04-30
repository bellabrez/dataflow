"""
Will look recursively in directory given in folder_name file for Bruker raw files.
If it finds one, it will set the ripper_done_file to be False.
"""

import os

def main():
    ripper_done_file = "C:/Users/User/projects/dataflow/scripts/batch_communicate/ripper_done.txt"
    folder_name = "C:/Users/User/projects/dataflow/scripts/batch_communicate/folder_name.txt"

    with open(folder_name, 'r') as file:
        directory = file.read()

    # Start with assuming ripper is done, unless we find a rawfile (then will be changed to False)
    with open(ripper_done_file, 'w') as file:
        file.write('True')

    check_for_raw_file(directory)

def check_for_raw_file(directory): 
    for item in os.listdir(directory):
        new_path = directory + '/' + item

        # Check if item is a directory
        if os.path.isdir(new_path):
            check_for_raw_file(new_path)
            
        # If the item is a file
        else:
            if '_RAWDATA_' in item:
                with open(ripper_done_file, 'w') as file:
                    file.write('False')
                break

if __name__ == "__main__":
    main()