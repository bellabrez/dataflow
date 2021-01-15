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

def main(args):

	logfile = args['logfile']
	printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

	#####################
	### Load Clusters ###
	#####################
	n_clusters = 2000
	labels_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/final_9_cluster_labels_2000.npy'
	cluster_model_labels = np.load(labels_file)

	############################
	### Load ALL Superslices ###
	############################
	pooled = np.zeros((2000, 49, 3384, 9))
	for z in range(49):
		printlog(str(z))
		brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/superslice_{}.nii".format(z) #<---------- !!!
		brain = np.array(nib.load(brain_file).get_data(), copy=True)
		fly_idx_delete = 3 #(fly_095)
		brain = np.delete(brain, fly_idx_delete, axis=-1) #### DELETING FLY_095 ####
		#(256, 128, 3384, 9)
		brain = np.reshape(brain,(-1,3384,9))
		# (32768, 3384, 9)
		signals = []
		for cluster_num in range(n_clusters):
			cluster_indicies = np.where(cluster_model_labels[z,:]==cluster_num)[0]
			mean_signal = np.mean(brain[cluster_indicies,:,:], axis=0)
			signals.append(mean_signal)
		signals=np.asarray(signals)
		#(2000, 3384, 9)
		pooled[:,z,:,:] = signals

	save_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210115_super_brain/20210115_super_brain'
	np.save(save_file, pooled)
	printlog('SAVED!')

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))