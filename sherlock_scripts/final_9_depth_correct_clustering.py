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
import umap
import psutil
import pickle

def main(args):

	logfile = args['logfile']
	printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

	cluster_dir = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210130_superv_depth_correction'
	depth_file = os.path.join(cluster_dir, 'depth_correction.npy')
	depth_correction = np.load(depth_file)

	def create_clusters(brain, n_clusters, cluster_dir):
		t0 = time.time()
		super_to_cluster = brain.reshape(-1, 3384*9)
		connectivity = grid_to_graph(256,128)
		cluster_model = AgglomerativeClustering(n_clusters=n_clusters,
										memory=cluster_dir,
										linkage='ward',
										connectivity=connectivity)
		cluster_model.fit(super_to_cluster)
		printlog('Duration: {}'.format(time.time()-t0))
		return cluster_model

	labels = {}
	for z in range(49):
		printlog(z)
		brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/superslice_{}.nii".format(z)
		brain = np.array(nib.load(brain_file).get_data(), copy=True)
		brain = np.delete(brain, fly_idx_delete, axis=-1) #### DELETING FLY_095 ####

		n_clusters = int(1000 * depth_correction[z])
		printlog(f'n_clusters: {n_clusters}')
		cluster_model = create_clusters(brain, n_clusters, cluster_dir)
		labels[z] = cluster_model.labels_
	   
	save_file = os.path.join(cluster_dir, 'labels.pickle')
	with open(save_file, 'wb') as handle:
		pickle.dump(labels, handle, protocol=pickle.HIGHEST_PROTOCOL)
	printlog('SAVED')

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))
