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

        # delete partial brains
        [os.remove(file) for file in channel]

        ##### Perform bleaching correction and z-scoring #####

        # Bleaching correction (per voxel)
        brain = bbb.bleaching_correction(stitched_brain)
        stitched_brain = None

        # Z-score brain
        brain = bbb.z_score_brain(brain)
        zbrain_file = os.path.join(os.path.split(directory)[0], 'brain_zscored_{}.nii'.format(colors[i]))
        bbb.save_brain(zbrain_file, brain)

    # Finally, stitch motcorr params and create motcorr graph
    save_motion_figure(transform_matrix, directory, motcorr_directory)
if __name__ == '__main__':
    main(sys.argv[1:])