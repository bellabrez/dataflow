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
    sort_nicely(greens)
    sort_nicely(reds)
    
    # add directory path
    reds = [os.path.join(directory, x) for x in reds]
    greens = [os.path.join(directory, x) for x in greens]

    # load brains
    channels = [reds, greens]
    colors = ['red', 'green']
    for i, channel in enumerate(channels):
        brains = []
        for brain_file in channel:
            brains.append(bbb.load_numpy_brain(brain_file))
        print('brains len: {}'.format(len(brains)))
        print('shape of first brain: {}'.format(np.shape(brains[0])))

        # Handle edgecase of single volume brain
        if len(np.shape(brain)) == 3:
            brain = brain[:,:,:,np.newaxis]
            
        stitched_brain = np.concatenate(brains, axis=-1)
        print('stitched_brain shape: {}'.format(np.shape(stitched_brain)))
        save_file = os.path.join(directory, 'stitched_brain_{}.nii'.format(colors[i]))
        bbb.save_brain(save_file, stitched_brain)

        # delete partial brains
        [os.remove(file) for file in channel]
        

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