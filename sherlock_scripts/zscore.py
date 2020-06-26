import os
import sys
import bigbadbrain as bbb
import numpy as np
import argparse
import subprocess

def main(args):

    logfile = args['logfile']
    directory = args['directory']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    moco_dir = os.path.join(directory, 'moco')

    for color in ['red', 'green']:
        brain_file = os.path.join(moco_dir, 'stitched_brain_{}.nii'.format(color))
        if path.exists(brain_file):
            printlog('Z-scoring: {}'.format(brain_file))
            brain = bbb.load_numpy_brain(brain_file)

            # Bleaching correction (per voxel)
            brain = bbb.bleaching_correction(brain)

            # Z-score brain
            brain = bbb.z_score_brain(brain)
            zbrain_file = os.path.join(directory, 'brain_zscored_{}.nii'.format(color))
            bbb.save_brain(zbrain_file, brain)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))