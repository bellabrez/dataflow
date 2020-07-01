import os
import sys
import numpy as np
import argparse
import subprocess
import json
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow

def main(args):

    logfile = args['logfile']
    directory = args['directory']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    moco_dir = os.path.join(directory, 'moco')

    for color in ['red', 'green']:
        brain_file = os.path.join(moco_dir, 'stitched_brain_{}.nii'.format(color))
        if os.path.exists(brain_file):
            printlog('Z-scoring: {}'.format(brain_file))

            brain = nib.load(file).get_data()
            brain = np.asarray(brain, dtype='float32')
            #brain = bbb.load_numpy_brain(brain_file)

            # Bleaching correction (per voxel)
            #brain = bbb.bleaching_correction(brain)
            smoothed = scipy.ndimage.gaussian_filter1d(brain,sigma=200,axis=-1,truncate=1)
            brain = brain - smoothed

            # Z-score brain
            #brain = bbb.z_score_brain(brain)
            brain_mean  = np.mean(brain, axis=3)
            brain_std = np.std(brain, axis=3)
            brain = (brain - brain_mean[:,:,:,None]) / brain_std[:,:,:,None]

            # Save brain
            zbrain_file = os.path.join(directory, 'brain_zscored_{}.nii'.format(color))
            #bbb.save_brain(zbrain_file, brain)
            aff = np.eye(4)
            img = nib.Nifti1Image(brain, aff)
            img.to_filename(file)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))