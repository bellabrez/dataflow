import os
import sys
import json
from time import sleep
import datetime
import bigbadbrain as bbb
import dataflow as flow
import numpy as np

def main(args):

    logfile = args['logfile']
    directory = args['directory'] # directory will be a full path to either an anat/imaging folder or a func/imaging folder
    dirtype = args['dirtype']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    if dirtype == 'func':
        files = ['functional_channel_1', 'functional_channel_2']
    elif dirtype == 'anat':
        files = ['anatomy_channel_1', 'anatomy_channel_2']

    for file in files:
        try:
            brain = bbb.load_numpy_brain(os.path.join(directory, file + '.nii'))
            meanbrain = np.mean(brain, axis=-1)
            save_file = os.path.join(directory, file + '_mean.nii')
            fly_func_str = ('|').join(directory.split('/')[-3:-1])
            printlog(f"{fly_func_str}|{file}|{brain.shape} --> {meanbrain.shape}")
            print(brain.shape[-1]) ### IMPORTANT: for communication to main
        except FileNotFoundError:
            printlog(f'{file} not found.')

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))