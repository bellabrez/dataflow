import numpy as np
import os
import sys
import psutil
import nibabel as nib
from time import time
import json
import dataflow as flow
import matplotlib.pyplot as plt
from contextlib import contextmanager
import warnings
warnings.filterwarnings("ignore")

def main(args):

    logfile = args['logfile']
    save_directory = args['save_directory']
    input_directory = args['input_directory']
    save_name = args['save_name']

    width = 120
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    ###################
    ### Load Brains ###
    ###################

    files = os.listdir(input_directory)
    bigbrain = np.zeros((len(files), 1024, 512, 256), dtype='float32',order='F')
    for i, file in enumerate(files):
        printlog(F"loading {file}")
        bigbrain[i,...] = np.asarray(nib.load(os.path.join(input_directory, file)).get_data(), dtype='float32')

    ###########
    ### Avg ###
    ###########

    meanbrain = np.mean(bigbrain, axis=0)

    ############
    ### Save ###
    ############

    save_file = os.path.join(save_directory, save_name + '.nii')
    nib.Nifti1Image(meanbrain, np.eye(4)).to_filename(save_file)
    printlog(F"Saved {save_file}")

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))