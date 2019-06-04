import os
import sys
import bigbadbrain as bbb
from time import sleep

def main():
    # Will look for and get folder that contains __done__
    # If multiple done folders, will get the oldest one (based on alphanumeric sorting)

    imports_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports'
    done_flag = '__done__'
    print('Checking for done flag.')
    done_folders = []
    for item in os.listdir(imports_path):
        if done_flag in item:
            print('Found flagged directory {}'.format(item))
            item_path = os.path.join(imports_path, item)
            done_folders.append(item_path)
    if len(done_folders) == 0:
        raise SystemExit
    else:
        bbb.sort_nicely(done_folders)
        # strip flag and pass directory name
        folder_stripped = done_folders[0].strip(done_flag)
        os.rename(done_folders[0], folder_stripped)
        sleep(20) # sleep to give system time to rename folder.
        os.system('sbatch build_fly.sh {}'.format(folder_stripped))

if __name__ == '__main__':
    main()
