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
	# to_umap = np.zeros((2000*49, 30456))
	# for z in range(49):
	# 	printlog(str(z))
	# 	brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/superslice_{}.nii".format(z) #<---------- !!!
	# 	brain = np.array(nib.load(brain_file).get_data(), copy=True)
	# 	fly_idx_delete = 3 #(fly_095)
	# 	brain = np.delete(brain, fly_idx_delete, axis=-1) #### DELETING FLY_095 ####
	# 	#(256, 128, 3384, 9)
	# 	brain = np.reshape(brain,(256*128,3384*9))
	# 	# (32768, 30456)
	# 	signals = []
	# 	for cluster_num in range(n_clusters):
	# 		cluster_indicies = np.where(cluster_model_labels[z,:]==cluster_num)[0]
	# 		mean_signal = np.mean(brain[cluster_indicies,:], axis=0)
	# 		signals.append(mean_signal)
	# 	signals=np.asarray(signals)
	# 	#(2000, 30456)
	# 	to_umap[z*2000:(z+1)*2000,:] = signals

	# save_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210103_super_brain'
	# np.save(save_file, to_umap)
	# printlog('SAVED!')
	load_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210103_super_brain/20210103_super_brain.npy'
	to_umap = np.load(load_file)

	t0 = time.time()
	reducer = umap.UMAP(n_neighbors=60, min_dist=0)
	embedding = reducer.fit_transform(to_umap.T)
	printlog('UMAP Duration: {}'.format(time.time()-t0))

	plt.figure(figsize=(10,10))
	plt.scatter(embedding[:,0], embedding[:,1])
	save_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/figs'
	timestr = time.strftime("%Y%m%d-%H%M%S")
	fname = os.path.join(save_path, f'{timestr}')
	plt.savefig(fname,dpi=300,bbox_inches='tight')

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))