import os
import sys
import json
from time import sleep
import datetime
import bigbadbrain as bbb
import dataflow as flow
import numpy as np
import nibabel as nib

import scipy
from skimage.filters import threshold_triangle as triangle
from sklearn.preprocessing import quantile_transform

from skimage.filters import unsharp_mask

def main(args):
    logfile = args['logfile']
    directory = args['directory'] # directory will be a full path anat/moco
    width = 120
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    ### Load brain ###
    file = os.path.join(directory, 'anat_red_clean.nii') 
    brain = np.asarray(nib.load(file).get_data(), dtype='float32')

    ### Sharpen ###
    brain_sharp = unsharp_mask(brain, radius=10, amount=.5)
    brain_sharp = unsharp_mask(brain_sharp, radius=5, amount=.5)
    brain_out = unsharp_mask(brain_sharp, radius=2, amount=.5)

    ### Save brain ###
    save_file = os.path.join(directory, 'anat_red_clean_sharp.nii')
    aff = np.eye(4)
    img = nib.Nifti1Image(brain_out, aff)
    img.to_filename(save_file)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))