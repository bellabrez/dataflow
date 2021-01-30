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

def main(args):

	logfile = args['logfile']
	printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

	memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
	printlog('Current memory usage: {:.2f}GB'.format(memory_usage))

	#####################
	### Load Clusters ###
	#####################
	# n_clusters = 2000
	# labels_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/final_9_cluster_labels_2000.npy'
	# cluster_model_labels = np.load(labels_file)

	#####################
	### Load Each fly ###
	#####################
	reduce_factor = 12
	dataset_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset"
	fly_names = ['fly_087', 'fly_089', 'fly_094', 'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_105']
	super_brain = np.zeros((256,128,49,int(3384/reduce_factor),9),dtype='float32')
	memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
	printlog('Current memory usage: {:.2f}GB'.format(memory_usage))

	for i,fly in enumerate(fly_names):
		printlog(fly)
		brain_file = os.path.join(dataset_path, fly, 'func_0', 'brain_zscored_green_high_pass_masked_warped.nii')
		super_brain[:,:,:,:,i] = np.array(nib.load(brain_file).get_data(), copy=True)[:,:,:,::reduce_factor]

		memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
		printlog('Current memory usage: {:.2f}GB'.format(memory_usage))

	printlog('reshaping brain...')
	super_brain = np.reshape(super_brain, (256*128*49,int(3384/reduce_factor)*9))
	printlog('done')

	t0 = time.time()
	clustering_dir = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210128_superv_simul_full_vol"
	connectivity = grid_to_graph(256,128,49)
	n_clusters = 30000
	cluster_model = AgglomerativeClustering(n_clusters=n_clusters,
									memory=clustering_dir,
									linkage='ward',
									connectivity=connectivity)
	cluster_model.fit(super_brain)
	printlog('DONE. Duration: {}'.format(time.time()-t0))

	save_file = os.path.join(clustering_dir, 'cluster_labels')
	np.save(save_file, cluster_model.labels_)
	printlog('SAVED.')

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))
