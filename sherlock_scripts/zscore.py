import os
import sys
import bigbadbrain as bbb
import numpy as np
import argparse
import datadir_appender

##### Perform bleaching correction and z-scoring #####

def main(args):
    print('args.directory: {}'.format(args.directory))
    print('args.channels: {}'.format(args.channels))

    directory = args.directory
    if args.datadir:
        directory = datadir_appender.datadir_appender(directory)
    if args.channels == 'rg':
        colors = ['red', 'green']
        print('Using red and green channels.')
    elif args.channels == 'r':
        colors = ['red']
        print('Using red channel.')
    elif args.channels == 'g':
        colors = ['green']
        print('Using green channel.')
    
    for color in colors:
        brain = bbb.load_numpy_brain(os.path.join(directory, 'stitched_brain_{}.nii'.format(color)))

        # Bleaching correction (per voxel)
        brain = bbb.bleaching_correction(brain)

        # Z-score brain
        brain = bbb.z_score_brain(brain)
        zbrain_file = os.path.join(os.path.split(directory)[0], 'brain_zscored_{}.nii'.format(color))
        bbb.save_brain(zbrain_file, brain)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='moco directory containing brains to z_score')
    parser.add_argument('-c', '--channels', choices=['r','g','rg'],
                        help="which brain channels to use", type=str)
    parser.add_argument('--datadir', action='store_true',
                        help='append supplied directory to Lukes data directory')
    args = parser.parse_args()
    main(args)