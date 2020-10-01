import os
import sys
import numpy as np
import argparse
import subprocess
import json
import time
import scipy
from scipy.ndimage import gaussian_filter1d
from skimage.filters import threshold_triangle as triangle
from sklearn.linear_model import LassoCV
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow

def main(args):

    logfile = args['logfile']
    directory = args['directory'] # full fly func path
    pca_subfolder = args['pca_subfolder']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    ### Load PCA ###
    pca_directory = os.path.join(directory, 'pca', pca_subfolder)
    printlog("performing glm on {}".format(pca_directory))
    file = os.path.join(pca_directory, 'scores_(spatial).npy')
    pca_spatial = np.load(file)
    file = os.path.join(pca_directory, 'loadings_(temporal).npy')
    pca_loadings = np.load(file)

    ### Load Fictrac and Timstamps###
    timestamps = bbb.load_timestamps(os.path.join(directory, 'imaging'))
    fictrac_raw = bbb.load_fictrac(os.path.join(directory, 'fictrac'))

    ### Prepare Fictrac ###
    resolution = 100 #desired resolution in ms
    expt_len = 1000*30*60
    fps = 50 #of fictrac camera
    behaviors = ['dRotLabY', 'dRotLabZ']
    fictrac = {}
    for behavior in behaviors:
        if behavior == 'dRotLabY': short = 'Y'
        elif behavior == 'dRotLabZ': short = 'Z'
        fictrac[short] = bbb.smooth_and_interp_fictrac(fictrac_raw,
                                                       fps,
                                                       resolution,
                                                       expt_len,
                                                       behavior,
                                                       timestamps=timestamps,
                                                       smoothing=51)
        fictrac[short] = fictrac[short]/np.std(fictrac[short])
    xnew = np.arange(0,expt_len,resolution)

    ### Fit GLM ###
    Y_glm = {}
    Y_glm['Y'] = fictrac['Y'].copy()
    Y_glm['Z'] = np.abs(fictrac['Z'].copy())

    models = {}
    num_pcs = 1000
    behaviors = ['Y', 'Z']
    for behavior in behaviors:
        t0 = time.time()
        models[behavior] = {'num_pcs': num_pcs, 'model': LassoCV()}
        X_glm = pca_loadings[:,:num_pcs]
        models[behavior]['model'].fit(X_glm, Y_glm[behavior])
        models[behavior]['score'] = models[behavior]['model'].score(X_glm, Y_glm[behavior])

        ### Construct Spatial Map ###
        coef = models[behavior]['model'].coef_
        spatial_map = np.tensordot(coef, pca_spatial[:1000,:,:,:],axes=1)

        ### Save map ###
        glm_directory = os.path.join(directory, 'glm')
        if not os.path.exists(glm_directory):
            os.mkdir(glm_directory)

        save_file = os.path.join(glm_directory, '20200930_{}.nii'.format(behavior))
        nib.Nifti1Image(spatial_map, np.eye(4)).to_filename(save_file)

        ### Save scores ###
        score_file = os.path.join(glm_directory, '20200930_score_{}.txt'.format(behavior))
        with open(score_file, "a") as f:
            f.write("{}:{}".format(behavior, models[behavior]['score']))

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))