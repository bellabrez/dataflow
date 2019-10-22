import os
import sys
import bigbadbrain as bbb
from time import sleep
import datetime

def main():
    # Will look for and get folder that contains __done__
    # If multiple done folders, will get the oldest one (based on alphanumeric sorting)

    imports_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports/build_queue'
    #done_flag = '__done__'
    print('Checking build queue.')
    print('Time: {}'.format(datetime.datetime.now()))
    queued_folders = []
    for item in os.listdir(imports_path):
        print('Found queued folder {}'.format(item))
        #item_path = os.path.join(imports_path, item)
        queued_folders.append(item)
    if len(queued_folders) == 0:
        print('No queued folders found. Raising SystemExit.')
        raise SystemExit
    else:
        bbb.sort_nicely(queued_folders)
        # strip flag and pass directory name
        #folder_stripped = queued_folders[0].strip(done_flag)
        #os.rename(queued_folders[0], folder_stripped)
        #sleep(20) # sleep to give system time to rename folder.
        folder_to_build = os.path.join(os.path.split(imports_path)[0], queued_folders[0])
        print('Passing control to build_fly.sh for folder {}'.format(folder_to_build))
        os.system('sbatch build_fly.sh {}'.format(folder_to_build))
        os.remove(os.path.join(imports_path, queued_folders[0]))

if __name__ == '__main__':
    main()
