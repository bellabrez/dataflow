import os
import sys
import subprocess

def main():
    imports_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports'
    done_flag = '__done__'
    print('Checking for done flag.')
    for item in os.listdir(imports_path):
        if done_flag in item:
            print('Found flagged directory {}'.format(item))
            item_path = os.path.join(imports_path, item)
            os.system("sbatch build_fly.sh")
            return
    raise SystemExit

if __name__ == '__main__':
    main()
