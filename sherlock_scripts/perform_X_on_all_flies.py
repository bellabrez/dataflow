import os
import sys
import numpy as np
from time import strftime
from shutil import copyfile
from xml.etree import ElementTree as ET
from lxml import etree, objectify
import bigbadbrain as bbb
import pandas as pd
import json
import bigbadbrain as bbb
from fly_builder import create_imaging_json

def main():
    print('Performing X on all flies')
    root_directory = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/'
    fly_folders = [os.path.join(root_directory,x) for x in os.listdir(root_directory) if 'fly' in x]
    bbb.sort_nicely(fly_folders)
    fly_folders = fly_folders[::-1]
    fly_folders = [os.path.join(root_directory, 'fly_54')]
    for fly in fly_folders:
        expt_folders = []
        expt_folders = [os.path.join(fly,x) for x in os.listdir(fly) if 'func' in x]
        if len(expt_folders) > 0:
            for expt_folder in expt_folders:
                create_imaging_json(os.path.join(expt_folder, 'imaging', 'functional.xml'))
                #bbb.perform_bleaching_analysis(expt_folder)

if __name__ == '__main__':
    main()