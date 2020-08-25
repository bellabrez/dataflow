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

def main(args):

    logfile = args['logfile']
    directory = args['directory'] # full fly func path
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    brain_path = os.path.join(directory, 'brain_zscored_green.nii')
    brain = np.asarray(nib.load(brain_path).get_data(), dtype='float32')

    timestamps = bbb.load_timestamps(os.path.join(directory, 'imaging'))
    fictrac = bbb.load_fictrac(os.path.join(directory, 'fictrac'))

    resolution = 10 #desired resolution in ms
    expt_len = 1000*30*60
    fps = 50 #of fictrac camera
    fictrac_interp = interp_fictrac(fictrac, fps, resolution, expt_len, timestamps)
    xnew = np.arange(0,expt_len,resolution)

    printlog("Performing Correlation on {}".format(brain_path))
    corr_brain = np.zeros((256,128,49))
    for z in range(49):
        for i in range(256):
            for j in range(128):
                corr_brain[i,j,z] = scipy.stats.pearsonr(fictrac_interp, brain[i,j,z,:])[0]

    corr_directory = os.path.join(directory, 'corr')
    if not os.path.exists(corr_directory):
        os.mkdir(corr_directory)

    save_file = os.path.join(corr_directory, 'corr_all_v.nii')
    nib.Nifti1Image(corr_brain, np.eye(4)).to_filename(save_file)
    
def interp_fictrac(fictrac, fps, resolution, expt_len, timestamps):
    camera_rate = 1/fps * 1000 # camera frame rate in ms
    
    x_original = np.arange(0,expt_len,camera_rate)
    
    dx = np.asarray(fictrac['dRotLabX'])
    dy = np.asarray(fictrac['dRotLabY'])
    dz = np.asarray(fictrac['dRotLabZ'])
    dx = scipy.signal.savgol_filter(dx,25,3)
    dy = scipy.signal.savgol_filter(dy,25,3)
    dz = scipy.signal.savgol_filter(dz,25,3)
    fictrac_smoothed = np.sqrt(dx*dx + dy*dy + dz*dz)
    
    fictrac_smoothed = np.abs(fictrac_smoothed)
    fictrac_interp_temp = interp1d(x_original, fictrac_smoothed, bounds_error = False)
    xnew = np.arange(0,expt_len,resolution) #0 to last time at subsample res
    fictrac_interp = fictrac_interp_temp(timestamps[:,25])

    # Replace Nans with zeros (for later code)
    np.nan_to_num(fictrac_interp, copy=False);
    
    return fictrac_interp

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))