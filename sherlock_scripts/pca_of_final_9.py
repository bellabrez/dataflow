import os
import sys
import numpy as np
import argparse
import subprocess
import json
import time
from scipy.ndimage import gaussian_filter1d
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow

from sklearn.decomposition import PCA

def main(args):

    logfile = args['logfile']
    X_type = args['X_type']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    load_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210115_super_brain/20210115_super_brain.npy'
    brain = np.load(load_file)
    printlog('brain is shape {}'.format(brain.shape))
    # 2000,49,3384,9

    if X_type == 'single_slice':
        X = np.reshape(brain[:,20,:,:], (2000,3384*9))
        # 2000, 30456
        X = X.T
        # 30456, 2000
    else:
        X = np.reshape(brain, (2000*49,3384*9))
        # 98000, 30456
        X = X.T
        # 30456, 98000

    printlog('X is time by voxels {}'.format(X.shape))
    
    printlog('PCA START...')
    pca = PCA().fit(X)
    printlog('PCA COMPLETE')

    pca_scores = pca.components_
    printlog('Scores is PC by voxel {}'.format(pca_scores.shape))
    save_file = F'/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210115_super_brain/20210118_pca_scores_{X_type}.npy'
    np.save(save_file, pca_scores)

    pca_loadings = pca.transform(X)
    printlog('Loadings is time by PC {}'.format(pca_loadings.shape))
    save_file = F'/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210115_super_brain/20210118_pca_loadings_{X_type}.npy'
    np.save(save_file, pca_loadings)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))