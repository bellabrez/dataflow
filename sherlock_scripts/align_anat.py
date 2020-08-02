import numpy as np
import os
import sys
import psutil
import nibabel as nib
from time import time
import json
import matplotlib.pyplot as plt
from contextlib import contextmanager
import warnings
warnings.filterwarnings("ignore")

import platform
if platform.system() != 'Windows':
    sys.path.insert(0, '/home/users/brezovec/.local/lib/python3.6/site-packages/lib/python/')
    import ants

def main(args):

    logfile = args['logfile']
    save_directory = args['save_directory']
    fixed_path = args['fixed_path']
    moving_path = args['moving_path']
    fixed_fly = args['fixed_fly']
    moving_fly = args['moving_fly']
    type_of_transform = args['type_of_transform'] # SyN or Affine
    width = 120
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    ###################
    ### Load Brains ###
    ###################

    fixed = ants.from_numpy(np.asarray(nib.load(fixed_path).get_data(), dtype='float32'))
    moving = ants.from_numpy(np.asarray(nib.load(moving_path).get_data(), dtype='float32'))

    #############
    ### Align ###
    #############

    t0=time()
    with stderr_redirected(): # to prevent dumb itk gaussian error bullshit infinite printing
        moco = ants.registration(fixed, moving, type_of_transform=type_of_transform)
    printlog('Fixed: {}, {} | Moving: {}, {} | {} | {}'.format(fixed_fly, fixed_path.split('/')[-1], moving_fly, moving_path.split('/')[-1], type_of_transform, sec_to_hms(time()-t0)))

    ############
    ### Save ###
    ############

    save_file = os.path.join(save_directory, moving_fly + '2' + fixed_fly + '.nii')
    nib.Nifti1Image(motCorr_vol['warpedmovout'].numpy(), np.eye(4)).to_filename(save_file)

def sec_to_hms(t):
        secs=F"{np.floor(t%60):02.0f}"
        mins=F"{np.floor((t/60)%60):02.0f}"
        hrs=F"{np.floor((t/3600)%60):02.0f}"
        return ':'.join([hrs, mins, secs])

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))