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

    # renormalize to .3-.7
    a = .3
    b = .7
    brain_input = a + (brain)*(b-a)

    # sharpen
    brain_sharp = unsharp_mask(brain_input, radius=3, amount=7)

    # make background nan
    brain_copy = brain_sharp.copy()
    brain_copy[np.where(brain_input < .31)] = np.nan

    # renormalize via quantile
    brain_out = quantile_transform(brain_copy.flatten().reshape(-1, 1), n_quantiles=500, random_state=0, copy=True)
    brain_out = brain_out.reshape(brain.shape);
    np.nan_to_num(brain_out, copy=False);

    ### Save brain ###
    save_file = os.path.join(directory, 'anat_red_clean_sharp.nii')
    aff = np.eye(4)
    img = nib.Nifti1Image(brain_out, aff)
    img.to_filename(save_file)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))