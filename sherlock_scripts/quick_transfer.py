import time
import sys
import os
import re
import json
import datetime
import pyfiglet
import textwrap
import dataflow as flow
from shutil import copyfile

flies = ['fly_' + str(x).zfill(3) for x in list(range(84,112))]
dataset_dir = "/Volumes/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset"
target_dir = "/Users/lukebrezovec/Downloads/20200801_brains"

for fly in flies:
    try:
        print(fly)
        source_path = os.path.join(dataset_dir, fly, 'anat_0', 'moco', 'stitched_brain_red_mean.nii')
        target_path = os.path.join(target_dir, fly + '.nii')
        copyfile(source_path, target_path)
        print("Done: {}".format(fly))
    except FileNotFoundError:
        print(F"Not found :{fly}")