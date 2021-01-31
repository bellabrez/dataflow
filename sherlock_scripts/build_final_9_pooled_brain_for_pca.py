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
import pickle

def main(args):

	logfile = args['logfile']
	printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

	#####################
	### Load Clusters ###
	#####################
	# new variable number based on depth
	labels_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210130_superv_depth_correction/labels.pickle'
	with open(labels_file, 'rb') as handle:
		cluster_model_labels = pickle.load(handle)

	############################
	### Load ALL Superslices ###
	############################
	#pooled = np.zeros((2000, 49, 3384, 9))
	pooled = {}
	for z in range(49):
		printlog(str(z))
		memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
		printlog('Current memory usage: {:.2f}GB'.format(memory_usage))
		brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/superslice_{}.nii".format(z) #<---------- !!!
		brain = np.array(nib.load(brain_file).get_data())#, copy=True)
		fly_idx_delete = 3 #(fly_095)
		brain = np.delete(brain, fly_idx_delete, axis=-1) #### DELETING FLY_095 ####
		#(256, 128, 3384, 9)
		brain = np.reshape(brain,(-1,3384,9))
		# (32768, 3384, 9)
		signals = []
		for cluster_num in range(len(cluster_model_labels[z])):
			cluster_indicies = np.where(cluster_model_labels[z]==cluster_num)[0]
			mean_signal = np.mean(brain[cluster_indicies,:,:], axis=0)
			signals.append(mean_signal)
		signals=np.asarray(signals)
		#(n_clusters, 3384, 9)
		pooled[z] = signals
		#pooled[:,z,:,:] = signals
		brain = None

	save_dir = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210130_superv_depth_correction'
	save_file = os.path.join(save_dir, 'super_brain.pickle')
	with open(save_file, 'wb') as handle:
		pickle.dump(pooled, handle, protocol=pickle.HIGHEST_PROTOCOL)
	printlog('SAVED')

	# save_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210115_super_brain/20210115_super_brain'
	# np.save(save_file, pooled)
	# printlog('SAVED!')

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))