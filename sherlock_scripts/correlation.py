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

import scipy
from scipy.interpolate import interp1d

def main(args):

    logfile = args['logfile']
    directory = args['directory'] # full fly func path
    behavior = args['behavior']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    #brain_path = os.path.join(directory, 'brain_zscored_green.nii')
    brain_path = os.path.join(directory, 'brain_zscored_green_high_pass_masked.nii')
    brain = np.asarray(nib.load(brain_path).get_data(), dtype='float32')

    timestamps = bbb.load_timestamps(os.path.join(directory, 'imaging'))
    fictrac_raw = bbb.load_fictrac(os.path.join(directory, 'fictrac'))

    resolution = 10 #desired resolution in ms
    expt_len = 1000*30*60
    fps = 50 #of fictrac camera

    fictrac_interp = interp_fictrac(fictrac_raw, fps, resolution, expt_len, timestamps, behavior)
    xnew = np.arange(0,expt_len,resolution)

    printlog("Performing Correlation on {}; behavior: {}".format(brain_path, behavior))
    corr_brain = np.zeros((256,128,49))
    for z in range(49):
        for i in range(256):
            for j in range(128):
                corr_brain[i,j,z] = scipy.stats.pearsonr(fictrac_interp, brain[i,j,z,:])[0]

    corr_directory = os.path.join(directory, 'corr')
    if not os.path.exists(corr_directory):
        os.mkdir(corr_directory)

    save_file = os.path.join(corr_directory, '20201020_corr_{}.nii'.format(behavior))
    nib.Nifti1Image(corr_brain, np.eye(4)).to_filename(save_file)
    printlog("Saved {}".format(save_file))
    
def interp_fictrac(fictrac, fps, resolution, expt_len, timestamps, behavior):
    camera_rate = 1/fps * 1000 # camera frame rate in ms
    
    x_original = np.arange(0,expt_len,camera_rate)
    
    dx = np.asarray(fictrac['dRotLabX'])
    dy = np.asarray(fictrac['dRotLabY'])
    dz = np.asarray(fictrac['dRotLabZ'])
    dx = scipy.signal.savgol_filter(dx,25,3)
    dy = scipy.signal.savgol_filter(dy,25,3)
    dz = scipy.signal.savgol_filter(dz,25,3)
    #fictrac_smoothed = np.sqrt(dx*dx + dy*dy + dz*dz)

    if behavior == 'Y':
        fictrac_smoothed = dy
    if behavior == 'Z_abs':
        fictrac_smoothed = np.abs(dz)
    if behavior == 'Z_pos':
        fictrac_smoothed = np.clip(dz, a_min=0, a_max=None)
    if behavior == 'Z_neg':
        fictrac_smoothed = np.clip(dz, a_min=None, a_max=0)
    
    fictrac_smoothed = np.abs(fictrac_smoothed)
    fictrac_interp_temp = interp1d(x_original, fictrac_smoothed, bounds_error = False)
    xnew = np.arange(0,expt_len,resolution) #0 to last time at subsample res
    fictrac_interp = fictrac_interp_temp(timestamps[:,25])

    # Replace Nans with zeros (for later code)
    np.nan_to_num(fictrac_interp, copy=False);
    
    return fictrac_interp

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))