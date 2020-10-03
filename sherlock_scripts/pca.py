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
    directory = args['directory'] # full fly func path
    file = args['file']
    save_subfolder = args['save_subfolder']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    brain_path = os.path.join(directory, file)
    #brain_path = os.path.join(directory, 'brain_zscored_green.nii')
    printlog("Performing PCA on {}".format(brain_path))
    brain = np.asarray(nib.load(brain_path).get_data(), copy=True)
    dim_y, dim_x, dim_z, dim_t = brain.shape
    printlog('brain shape is x,y,z,t {}'.format(brain.shape))
    printlog('or, {} {} {} {}'.format(dim_y, dim_x, dim_z, dim_t))

    t0 = time.time()
    X = brain[:,:,:,:].reshape(-1,brain.shape[-1]).T
    brain = None
    printlog('X is time by voxels {}'.format(X.shape))
    printlog('Reshape duration: {}'.format(time.time()-t0))

    t0 = time.time()
    pca = PCA().fit(X)
    pca_scores = pca.components_
    printlog('Scores is PC by voxel {}'.format(pca_scores.shape))
    pca_loadings = pca.transform(X)
    printlog('Loadings is time by PC {}'.format(pca_loadings.shape))
    pca_spatial = np.reshape(pca_scores, (-1,dim_y,dim_x,dim_z))
    printlog('Spatial is {}'.format(pca_spatial.shape))
    printlog('PCA duration: {}'.format(time.time()-t0))

    pca_directory = os.path.join(directory, 'pca')
    if not os.path.exists(pca_directory):
        os.mkdir(pca_directory)

    if save_subfolder:
        pca_directory = os.path.join(pca_directory, save_subfolder)
        os.mkdir(pca_directory)

    save_file = os.path.join(pca_directory, 'scores_(spatial).npy')
    np.save(save_file, pca_spatial)
    save_file = os.path.join(pca_directory, 'loadings_(temporal).npy')
    np.save(save_file, pca_loadings)
    printlog('Saved PCA!')

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))