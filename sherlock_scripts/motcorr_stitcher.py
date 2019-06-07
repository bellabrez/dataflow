import os
import sys
import bigbadbrain as bbb
import numpy as np
import re

def main(args):
    print('Stitcher started.')
    directory = args[0]
    print('directory: {}'.format(directory))

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
    channels = [reds, greens]
    colors = ['red', 'green']

    # Do for red and green
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

    stitched_params = np.concatenate(motcorr_params, axis=0)
    save_file = os.path.join(directory, 'motcorr_params_stitched')
    np.save(save_file, stitched_params)
    [os.remove(file) for file in motcorr_param_files]
    xml_dir = os.path.join(os.path.split(directory)[0], 'imaging')
    bbb.save_motion_figure(stitched_params, xml_dir, directory)

    ### START Z-SCORING ###
    os.system("sbatch zscore.sh {}".format(directory))

if __name__ == '__main__':
    main(sys.argv[1:])