import os
import sys
import numpy as np
import argparse
import subprocess
import json
import time
from scipy.ndimage import gaussian_filter1d
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow

def main(args):

    logfile = args['logfile']
    directory = args['directory'] # full fly func path
    file = args['file']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    brain_file = os.path.join(directory, file)
    printlog("smoothing {}".format(file))
    
    ### Load Brain ###
    brain = np.asarray(nib.load(brain_file).get_data(), dtype='float32')

    ### Smooth ###
    printlog('smoothing')
    t0 = time.time()
    smoothed = gaussian_filter1d(brain,sigma=200,axis=-1,truncate=1)
    printlog("brain smoothed duration: ({})".format(time.time()-t0))

    ### Apply Smooth Correction ###
    t0 = time.time()
    brain_corrected = brain - smoothed + np.mean(brain, axis=3)[:,:,:,None] #need to add back in mean to preserve offset
    printlog("brain corrected duration: ({})".format(time.time()-t0))

    ### Save Brain ###
    corrected_brain_file = os.path.join(directory, 'brain_zscored_green_high_pass.nii')
    nib.Nifti1Image(brain_corrected, np.eye(4)).to_filename(corrected_brain_file)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))