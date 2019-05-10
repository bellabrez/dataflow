import os
import sys

def main():
    imports_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports'
    done_flag = '__done__'
    print('Checking for done flag.')
    for item in os.listdir(imports_path):
        if done_flag in item:
            print('Found flagged directory {}'.format(item))
            item_path = os.path.join(imports_path, item)
            return item_path
    return 'None'

if __name__ == '__main__':
    main()