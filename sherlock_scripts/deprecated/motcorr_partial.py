import sys
import os
import nibabel as nib
import numpy as np
import bigbadbrain as bbb
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, '/home/users/brezovec/.local/lib/python3.6/site-packages/lib/python/')
import ants

def main(args):
    directory = args[0]
    motcorr_directory = args[1]
    master_path = args[2]
    slave_path = args[3]
    master_path_mean = args[4]
    vol_start = int(args[5])
    vol_end = int(args[6])

    # For the sake of memory, lets try to load only the part of the brain we will need.
    master_brain = load_partial_brain(master_path,vol_start,vol_end)
    slave_brain = load_partial_brain(slave_path,vol_start,vol_end)
    mean_brain = ants.from_numpy(bbb.load_numpy_brain(master_path_mean))

    bbb.motion_correction(master_brain,
                          slave_brain,
                          directory,
                          motcorr_directory,
                          meanbrain=mean_brain,
                          suffix='_'+str(vol_start))

def load_partial_brain(file, start, stop):
    brain = nib.load(file).dataobj[:,:,:,start:stop]
    #brain = ants.from_numpy(np.asarray(np.squeeze(brain), 'float64'))
    brain = ants.from_numpy(np.asarray(np.squeeze(brain), dtype=np.uint16)) #updated dtype 20200624
    # always keep 4 axes:
    if len(np.shape(brain)) == 3:
      brain = brain[:,:,:,np.newaxis]
    return brain

if __name__ == '__main__':
    main(sys.argv[1:])