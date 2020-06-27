import os
import sys
import json
from time import sleep
import datetime
import bigbadbrain as bbb
import dataflow as flow
import numpy as np
import nibabel as nib

def main(args):

    logfile = args['logfile']
    directory = args['directory'] # directory will be a full path to either an anat/imaging folder or a func/imaging folder
    dirtype = args['dirtype']
    width = 120
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    if dirtype == 'func':
        files = ['functional_channel_1', 'functional_channel_2']
    elif dirtype == 'anat':
        files = ['anatomy_channel_1', 'anatomy_channel_2']

    for file in files:
        try:
            ### make mean ###
            brain = np.asarray(nib.load(os.path.join(directory, file + '.nii')).get_data(), dtype='uint16')
            meanbrain = np.mean(brain, axis=-1)

            ### Save ###
            save_file = os.path.join(directory, file + '_mean.nii')
            aff = np.eye(4)
            img = nib.Nifti1Image(meanbrain, aff)
            img.to_filename(save_file)

            fly_func_str = ('|').join(directory.split('/')[-3:-1])
            printlog(f"{fly_func_str} | {file} | {brain.shape} --> {meanbrain.shape}")
            print(brain.shape[-1]) ### IMPORTANT: for communication to main
        except FileNotFoundError:
            printlog(F"Not found (skipping){file:.>{width-20}}")
            #printlog(f'{file} not found.')

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))