import numpy as np
import sys
import os
import bigbadbrain as bbb
from sklearn.linear_model import LassoCV

def main(directory):

    ### Load PCA
    save_file = os.path.join(directory, 'pca', 'scores_(spatial).npy')
    pca_spatial = np.load(save_file)
    save_file = os.path.join(directory, 'pca', 'loadings_(temporal).npy')
    pca_loadings = np.load(save_file)

    ### Load timestamps
    timestamps = bbb.load_timestamps(os.path.join(directory, 'imaging'))

    ### Load fictrac
    fictrac_raw = bbb.load_fictrac(os.path.join(directory, 'fictrac'))
    fictrac = bbb.smooth_and_interp_fictrac(fictrac_raw, fps=50, resolution=10, expt_len=1000*30*60, behavior='dRotLabY')

    ### Fit model
    num_pcs = 100
    Y_glm = fictrac
    X_glm = pca_loadings[:,:num_pcs]

    model = LassoCV().fit(X_glm, Y_glm)
    score = model.score(X_glm, Y_glm)

    brain_map = np.tensordot(model.coef_, pca_spatial[:num_pcs,:,:,:],axes=1)
    
    pca_glm_directory = os.path.join(directory, 'pca_glm')
    if not os.path.exists(pca_glm_directory):
        os.mkdir(pca_glm_directory)
    
    save_file = os.path.join(pca_glm_directory, 'forward.nii')
    bbb.save_brain(save_file, brain_map)

if __name__ == '__main__':
    main(sys.argv[1])