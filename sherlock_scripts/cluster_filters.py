import os
import sys
import numpy as np
import argparse
import subprocess
import json
import time
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d
from sklearn.cluster import AgglomerativeClustering
from sklearn.feature_extraction.image import grid_to_graph
import scipy
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow
from scipy.fftpack import fft,fftshift,ifft

def main(args):
	logfile = args['logfile']
	printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

	main_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201221_neural_weighted_behavior/"

	response_files = [os.path.join(main_path, file) for file in os.listdir(main_path) if 'responses' in file]
	bbb.sort_nicely(response_files)

	responses = []
	for file in response_files:
	    responses.append(np.load(file))
	responses = np.asarray(responses)

	responses_split = np.reshape(responses, (49,2000,3,500))
	responses_fft = fft(responses_split,axis=-1)
	responses_fft[:,:,:,15:23] = 0
	responses_fft[:,:,:,475:485] = 0
	responses_filtered = ifft(responses_fft,axis=-1)

	to_fit = np.reshape(responses_filtered[:,:,:,:].real,(49*2000,3*500))
	printlog('to_fit shape: {}'.format(to_fit.shape))

	printlog('clustering.........')
	model = AgglomerativeClustering(distance_threshold=0,
	                                n_clusters=None,
	                                memory=main_path,
	                                linkage='ward')
	model = model.fit(to_fit)
	printlog('complete!')

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))