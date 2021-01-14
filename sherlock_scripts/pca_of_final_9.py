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
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    load_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210103_super_brain/20210103_super_brain.npy'
    X = np.load(load_file).T
    printlog('X is time by voxels {}'.format(X.shape))
    
    printlog('PCA START...')
    pca = PCA().fit(X)
    printlog('PCA COMPLETE')

    pca_scores = pca.components_
    printlog('Scores is PC by voxel {}'.format(pca_scores.shape))
    save_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210103_super_brain/20210114_pca_scores.npy'
    np.save(save_file, pca_scores)

    pca_loadings = pca.transform(X)
    printlog('Loadings is time by PC {}'.format(pca_loadings.shape))
    save_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210103_super_brain/20210114_pca_loadings.npy'
    np.save(save_file, pca_loadings)

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))