import sys
import numpy as np
import json
import time
import dataflow as flow
import pickle

from sklearn.decomposition import FastICA

def fastIca(signals,  alpha = 1, thresh=0.0001, iterations=200):
    m, n = signals.shape

    # Initialize random weights
    W = np.random.rand(m, m)

    for c in range(m):
        w = W[c, :].copy().reshape(m, 1)
        w = w / np.sqrt((w ** 2).sum())

        i = 0
        lim = 100
        while ((lim > thresh) & (i < iterations)):

            # Dot product of weight and signal
            ws = np.dot(w.T, signals)

            # Pass w*s into contrast function g
            wg = np.tanh(ws * alpha).T

            # Pass w*s into g prime
            wg_ = (1 - np.square(np.tanh(ws))) * alpha

            # Update weights
            wNew = (signals * wg.T).mean(axis=1) - wg_.mean() * w.squeeze()

            # Decorrelate weights              
            wNew = wNew - np.dot(np.dot(wNew, W[:c].T), W[:c])
            wNew = wNew / np.sqrt((wNew ** 2).sum())

            # Calculate limit condition
            lim = np.abs(np.abs((wNew * w).sum()) - 1)

            # Update weights
            w = wNew

            # Update counter
            i += 1

        W[c, :] = w.T
    return W

def main(args):

    logfile = args['logfile']
    #fly_idx = args['fly_idx']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    printlog('numpy: ' + str(np.__version__))

    load_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210130_superv_depth_correction/super_brain.pickle'
    with open(load_file, 'rb') as handle:
        temp_brain = pickle.load(handle)
    #brain is a dict of z, each containing a variable number of supervoxels
    #one dict element looks like: (n_clusters, 3384, 9)
    X = np.zeros((0,3384,9))
    #for z in range(49):
    for z in range(9,49-9):
        X = np.concatenate((X,temp_brain[z]),axis=0)

    printlog(str(X.shape))
    #printlog(F'X_type is {X_type}')
    X = np.swapaxes(X,1,2) # THIS LINE WAS MISSING
    #X = np.reshape(X,(30858, -1))
    X = np.reshape(X,(-1, 30456))
    X = X.T

    # there are 30456 timepoints

    printlog('X is time by voxels {}'.format(X.shape))
    # num_tp = 3384
    # start = fly_idx*num_tp
    # stop = (fly_idx+1)*num_tp
    # X = X[start:stop,:]
    # printlog(F'fly_idx: {fly_idx}, start: {start}, stop: {stop}')
    # printlog('After fly_idx, X is time by voxels {}'.format(X.shape))

    #transformer = FastICA(n_components=100)
    #X_transformed = transformer.fit_transform(X)

    printlog("running custom ICA")
    W = fastIca(X,  alpha=1)
    unMixed = X.T.dot(W.T)

    printlog('X_transformed is {}'.format(unMixed.shape))

    save_file = F'/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210130_superv_depth_correction/20221107_ICA_ztrim_fly.npy'
    np.save(save_file, unMixed)


if __name__ == '__main__':
    main(json.loads(sys.argv[1]))