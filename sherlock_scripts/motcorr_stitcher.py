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
        print('looking at: {}'.format(item))
        # sanity check that it is .nii
        if '.nii' in item:
            if 'red' in item:  
                reds.append(item)
            elif 'green' in item:
                greens.append(item)

    # need to order correctly for correct stitching
    print('reds: {}'.format(reds))
    print('greens: {}'.format(greens))
    greens = sort_nicely(greens)
    reds = sort_nicely(reds)
    print('reds: {}'.format(reds))
    print('greens: {}'.format(greens))
    
    # add directory path
    reds = [os.path.join(directory, x) for x in reds]
    greens = [os.path.join(directory, x) for x in greens]
    print('reds: {}'.format(reds))
    print('greens: {}'.format(greens))

    # load brains
    channels = [reds]
    for channel in channels:
        brains = []
        for brain_file in channel:
            brains.append(bbb.load_numpy_brain(brain_file))
        #brains = np.asarray(brains)
        print('brains shape: {}'.format(brains))
        #x = np.shape(brains)[1]
        #y = np.shape(brains)[2]
        #z = np.shape(brains)[3]
        #stitched_brain = np.reshape(brains, (x, y, z, -1))
        stitched_brain = np.concatenate(brains, axis=-1)
        print('stitched_brain shape: {}'.format(stitched_brain))
        save_file = os.path.join(directory, 'stitched_brain.nii')
        bbb.save_brain(save_file, stitched_brain)

def alphanum_key(s):
    """ Tries to change strs to ints. """
    return [tryint(c) for c in re.split('([0-9]+)', s)]

def sort_nicely(x):
    """

    Parameters
    ----------

    Returns
    -------

    """
    x.sort(key=alphanum_key)
    
def tryint(s):
    """ Tries to change a single str to an int. """

    try:
        return int(s)
    except:
        return s

if __name__ == '__main__':
    main(sys.argv[1:])