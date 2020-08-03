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
from scipy import ndimage
from skimage.filters import threshold_triangle as triangle
from sklearn.preprocessing import quantile_transform

def main(args):
    logfile = args['logfile']
    directory = args['directory'] # directory will be a full path anat/moco
    width = 120
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    ### Load brain ###
    brain = np.asarray(nib.load(os.path.join(directory, file + '.nii')).get_data(), dtype='float32')

    ### Blur brain and mask small values ###
    brain_copy = brain.copy().astype('float32')
    brain_copy = scipy.ndimage.filters.gaussian_filter(brain_copy, sigma=10)
    threshold = triangle(brain_copy)
    brain_copy[np.where(brain_copy < threshold/2)] = 0

    ### Remove blobs outside contiguous brain ###
    labels, label_nb = ndimage.label(brain_copy)
    brain_label = np.bincount(labels.flatten())[1:].argmax()+1
    brain_copy = brain.copy().astype('float32')
    brain_copy[np.where(labels != brain_label)] = 0

    ### Perform quantile normalization ###
    brain_3d = quantile_transform(brain_copy.flatten().reshape(-1, 1), n_quantiles=500, random_state=0, copy=True).reshape(brain.shape)

    ### Save brain ###
    save_file = os.path.join(directory, file + '_mean.nii')
    aff = np.eye(4)
    img = nib.Nifti1Image(meanbrain, aff)
    img.to_filename(save_file)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))