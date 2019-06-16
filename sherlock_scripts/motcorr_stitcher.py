import os
import sys
import bigbadbrain as bbb
import numpy as np
import re
import argparse
import datadir_appender

def main(args):
    print('Stitcher started.')
    directory = args.directory
    print('directory: {}'.format(directory))

    if args.datadir:
        directory = datadir_appender.datadir_appender(directory)
    if args.channels == 'rg':
        colors = ['red', 'green']
        channels = [reds, greens]
        print('Using red and green channels.')
    elif args.channels == 'r':
        colors = ['red']
        channels = [reds]
        print('Using red channel.')
    elif args.channels == 'g':
        colors = ['green']
        channels = [greens]
        print('Using green channel.')

    # directory will contain motcorr_green_x.nii and motcorr_red_x.nii
    # get list of reds and greens
    reds = []
    greens = []
    for item in os.listdir(directory):
        # sanity check that it is .nii
        if '.nii' in item:
            if 'red' in item:  
                reds.append(item)
            elif 'green' in item:
                greens.append(item)

    # need to order correctly for correct stitching
    bbb.sort_nicely(greens)
    bbb.sort_nicely(reds)
    
    # add directory path
    reds = [os.path.join(directory, x) for x in reds]
    greens = [os.path.join(directory, x) for x in greens]

    ### load brains ###
    # This part in based on the input argparse
    for i, channel in enumerate(channels):
        brains = []
        for brain_file in channel:
            brain = bbb.load_numpy_brain(brain_file)

            # Handle edgecase of single volume brain
            if len(np.shape(brain)) == 3:
                brain = brain[:,:,:,np.newaxis]
            print('shape of partial brain: {}'.format(np.shape(brain)))
            brains.append(brain)

        print('brains len: {}'.format(len(brains)))
        stitched_brain = np.concatenate(brains, axis=-1)
        print('stitched_brain shape: {}'.format(np.shape(stitched_brain)))
        save_file = os.path.join(directory, 'stitched_brain_{}.nii'.format(colors[i]))
        bbb.save_brain(save_file, stitched_brain)
        stitched_brain = None

        # delete partial brains
        [os.remove(file) for file in channel]

    ### Stitch motcorr params and create motcorr graph
    # get motcorr param files
    motcorr_param_files = []
    for item in os.listdir(directory):
        if '.npy' in item:
            file = os.path.join(directory, item)
            motcorr_param_files.append(file)
    bbb.sort_nicely(motcorr_param_files)
    
    # Load motcorr param files (needed to sort first)
    motcorr_params = []
    for file in motcorr_param_files:
        motcorr_params.append(np.load(file))

    if len(motcorr_params) > 0:
        stitched_params = np.concatenate(motcorr_params, axis=0)
        save_file = os.path.join(directory, 'motcorr_params_stitched')
        np.save(save_file, stitched_params)
        [os.remove(file) for file in motcorr_param_files]
        xml_dir = os.path.join(os.path.split(directory)[0], 'imaging')
        print('directory: {}'.format(directory))
        print('xml_dir: {}'.format(xml_dir))
        sys.stdout.flush()
        bbb.save_motion_figure(stitched_params, xml_dir, directory)
    else:
        print('Empty motcorr params - skipping saving moco figure.')

    ### START Z-SCORING ###
    os.system("sbatch zscore.sh {}".format(directory))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='moco directory containing brains to z_score')
    parser.add_argument('-c', '--channels', choices=['r','g','rg'],
                        help="which brain channels to use", type=str)
    parser.add_argument('--datadir', action='store_true',
                        help='append supplied directory to Lukes data directory')
    args = parser.parse_args()
    main(args)