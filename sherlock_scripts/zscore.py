import os
import sys
import bigbadbrain as bbb
import numpy as np

##### Perform bleaching correction and z-scoring #####

def main(args):
    directory = args[0]
    # this motcorr directory will contain stitched_brain_red.nii and green
    colors = ['red', 'green']
    for color in colors:
        brain = bbb.load_numpy_brain(os.path.join(directory, 'stitched_brain_{}.nii'.format(color)))

        # Bleaching correction (per voxel)
        brain = bbb.bleaching_correction(brain)

        # Z-score brain
        brain = bbb.z_score_brain(brain)
        zbrain_file = os.path.join(os.path.split(directory)[0], 'brain_zscored_{}.nii'.format(color))
        bbb.save_brain(zbrain_file, brain)

if __name__ == '__main__':
    main(sys.argv[1:])