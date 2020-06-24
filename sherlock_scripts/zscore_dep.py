import os
import sys
import bigbadbrain as bbb
import numpy as np
import argparse
import datadir_appender
import subprocess

##### Perform bleaching correction and z-scoring #####

##### THEN, LAUNCHES QC SCRIPTS #####

def main(args):
    print('args.directory: {}'.format(args.directory))
    print('args.channels: {}'.format(args.channels))

    directory = args.directory
    if args.datadir:
        directory = datadir_appender.datadir_appender(directory)
        print('datadir_appender made directory into: {}'.format(directory))
    if args.channels == 'rg':
        colors = ['red', 'green']
        print('Using red and green channels.')
    elif args.channels == 'r':
        colors = ['red']
        print('Using red channel.')
    elif args.channels == 'g':
        colors = ['green']
        print('Using green channel.')
    elif args.channels is None:
        colors = ['red', 'green']
        print('Using red and green channels.')
    
    for color in colors:
        print('loading brain from {}'.format(directory))
        brain = bbb.load_numpy_brain(os.path.join(directory, 'stitched_brain_{}.nii'.format(color)))

        # Bleaching correction (per voxel)
        brain = bbb.bleaching_correction(brain)

        # Z-score brain
        brain = bbb.z_score_brain(brain)
        zbrain_file = os.path.join(os.path.split(directory)[0], 'brain_zscored_{}.nii'.format(color))
        bbb.save_brain(zbrain_file, brain)

    ################################
    ### Create bleaching figures ###
    ################################
    os.system("sbatch bleaching_qc.sh {}".format(os.path.split(directory)[0]))

    ###################
    ### Perform PCA ###
    ###################
    jobid = subprocess.check_output('sbatch pca.sh {}'.format(os.path.split(directory)[0]),shell=True)
    # Get job ids so we can use them as dependencies
    jobid_str = jobid.decode('utf-8')
    jobid_str = [x for x in jobid_str.split() if x.isdigit()][0]
    print('jobid: {}'.format(jobid_str))
    job_ids = []
    job_ids.append(jobid_str)
    # Create weird job string slurm wants
    job_ids_colons = ':'.join(job_ids)
    print('Colons: {}'.format(job_ids_colons))

    ########################################
    ### Once PCA done, perform quick GLM ###
    ########################################
    os.system("sbatch --dependency=afterany:{} quick_glm.sh {}".format(job_ids_colons, os.path.split(directory)[0]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='moco directory containing brains to z_score')
    parser.add_argument('-c', '--channels', choices=['r','g','rg'],
                        help="which brain channels to use", type=str)
    parser.add_argument('--datadir', action='store_true',
                        help='append supplied directory to Lukes data directory')
    args = parser.parse_args()
    main(args)