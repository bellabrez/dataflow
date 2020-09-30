import os
import sys
import numpy as np
import argparse
import subprocess
import json
import time
import scipy
from scipy.ndimage import gaussian_filter1d
from skimage.filters import threshold_triangle as triangle
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow

def main(args):

    logfile = args['logfile']
    directory = args['directory'] # full fly func path
    file = args['file']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    brain_file = os.path.join(directory, file)
    printlog("masking {}".format(file))
    
    ### Load Brain ###
    brain = np.array(nib.load(brain_file).get_data(), copy=True)

    ### Load brain to use as mask ###
    brain_file = os.path.join(directory, 'imaging', 'functional_channel_2_mean.nii')
    brain_mean = np.array(nib.load(brain_file).get_data(), copy=True)

    ### Mask ###
    printlog('masking')
    threshold = triangle(brain_mean)
    brain_mean[np.where(brain_mean < threshold/1.3)] = 0

    labels, label_nb = scipy.ndimage.label(brain_mean)
    brain_label = np.bincount(labels.flatten())[1:].argmax()+1

    mask = np.ones(brain_mean.shape)
    mask[np.where(labels != brain_label)] = 0 # np.nan here failed with PCA

    brain = brain*mask[:,:,:,None]

    ### Save Brain ###
    brain_save_file = os.path.join(directory, 'brain_zscored_green_high_pass_masked.nii')
    nib.Nifti1Image(brain, np.eye(4)).to_filename(brain_save_file)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))