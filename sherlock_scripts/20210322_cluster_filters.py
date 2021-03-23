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
from scipy.cluster.hierarchy import dendrogram
from sklearn.feature_extraction.image import grid_to_graph
import scipy
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow

def main(args):
	logfile = args['logfile']
	printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

	n_clusters = 2000
	labels_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/cluster_labels.npy'
	cluster_model_labels = np.load(labels_file)

	################################
	### Load and correct filters ###
	################################
	main_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210316_neural_weighted_behavior"

	response_files = [os.path.join(main_path, file) for file in os.listdir(main_path) if 'responses' in file]
	bbb.sort_nicely(response_files)

	responses = []
	for file in response_files:
		responses.append(np.load(file))
	responses = np.asarray(responses)
	responses.shape

	responses_split = np.reshape(responses, (49-18,2000,4,500))
	responses_fft = fft(responses_split,axis=-1)
	responses_fft[:,:,:,15:23] = 0
	responses_fft[:,:,:,475:485] = 0
	responses_filtered = ifft(responses_fft,axis=-1)
	responses_filtered = responses_filtered.real

	#################
	### NORMALIZE ###
	#################
	all_signals = np.reshape(responses_filtered[:,:,:,:],(31*2000,4,500))
	# (62000,4,500)
	# want to exclude signals that have no response to any behavior
	# each behavior type will have a different distribution of sum(abs(signal))
	all_sums = np.sum(np.abs(all_signals),axis=-1)

	# (62000,4)
	# how to pick the threshold for each behavior?
	# lets aim to use corr map sig threshold,
	# but for now take top 25%
	thresholds = np.percentile(all_sums,75,axis=0)
	all_signals[(all_sums<thresholds[np.newaxis,:])] = 0

	all_maxs = np.max(np.abs(all_signals),axis=-1)
	all_signals_normalized = all_signals/all_maxs[:,:,np.newaxis]
	all_signals_normalized = np.nan_to_num(all_signals_normalized)

	to_fit = np.reshape(all_signals_normalized, (62000,2000))

	###############
	### CLUSTER ###
	###############
	t0 = time.time()
	printlog('clustering.........')
	model = AgglomerativeClustering(distance_threshold=0,
									n_clusters=None,
									memory=main_path,
									linkage='ward')
	model = model.fit(to_fit)
	printlog('complete!')
	printlog(str(time.time()-t0))

	### Create linkage matrix for dendrogram
	counts = np.zeros(model.children_.shape[0])
	n_samples = len(model.labels_)
	for i, merge in enumerate(model.children_):
		current_count = 0
		for child_idx in merge:
			if child_idx < n_samples:
				current_count += 1  # leaf node
			else:
				current_count += counts[child_idx - n_samples]
		counts[i] = current_count

	linkage_matrix = np.column_stack([model.children_, model.distances_,
									  counts]).astype(float)

	test = dendrogram(linkage_matrix,
		   truncate_mode=None,
		   p=10,
		   color_threshold=None,
		   #link_color_func=lambda x: colors[x],
		   no_labels=True,
		   distance_sort=True,
		   no_plot=True);

	printlog('did not fail!')


if __name__ == '__main__':
	main(json.loads(sys.argv[1]))	 