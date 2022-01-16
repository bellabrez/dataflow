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

def main(args):
	logfile = args['logfile']
	#z = args['z']
	printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

	fly_names = ['fly_087', 'fly_089', 'fly_094', 'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_105']
	dataset_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset"
	expt_len = 1000*30*60
	resolution = 10
	high_res_timepoints = np.arange(0,expt_len,resolution) #0 to last time at subsample res

	class Fly:
		def __init__ (self, fly_name, fly_idx):
			self.dir = os.path.join(dataset_path, fly_name, 'func_0')
			self.fly_idx = fly_idx
			self.fly_name = fly_name
			self.maps = {}
		def load_timestamps (self):
			self.timestamps = bbb.load_timestamps(os.path.join(self.dir, 'imaging'))
		def load_fictrac (self):
			self.fictrac = Fictrac(self.dir, self.timestamps)
		def load_brain_slice (self):
			self.brain = brain[:,:,:,self.fly_idx]
		def load_anatomy (self):
			to_load = os.path.join(dataset_path, self.fly_name, 'warp', 'anat-to-meanbrain.nii')
			self.anatomy = np.array(nib.load(to_load).get_data(), copy=True)
		def load_z_depth_correction (self):
			to_load = os.path.join(dataset_path, self.fly_name, 'warp', '20201220_warped_z_depth.nii')
			self.z_correction = np.array(nib.load(to_load).get_data(), copy=True)
		def get_cluster_averages (self, cluster_model_labels, n_clusters):
			neural_data = self.brain.reshape(-1, 3384)
			signals = []
			self.cluster_indicies = []
			for cluster_num in range(n_clusters):
				cluster_indicies = np.where(cluster_model_labels==cluster_num)[0]
				mean_signal = np.mean(neural_data[cluster_indicies,:], axis=0)
				signals.append(mean_signal)
				self.cluster_indicies.append(cluster_indicies) # store for later
			self.cluster_signals=np.asarray(signals)
		def get_cluster_id (self, x, y):
			ax_vec = x*128 + y
			for i in range(n_clusters):
				if ax_vec in self.cluster_indicies[i]:
					cluster_id = i
					break
			return cluster_id

	#####################
	### Load Master X ###
	#####################
	file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210316_neural_weighted_behavior/master_X_jerk.npy"
	printlog(f'loading {file}')
	X = np.load(file)

	#####################
	### Make Clusters ###
	#####################
	n_clusters = 2000
	labels_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/cluster_labels.npy'
	cluster_model_labels_all = np.load(labels_file)

	###################
	### Build Flies ###
	###################
	flies = {}
	for i, fly in enumerate(fly_names):
		flies[fly] = Fly(fly_name=fly, fly_idx=i)
		flies[fly].load_timestamps()
		flies[fly].load_z_depth_correction()

	for z in range(9,49-9):
		printlog(f"Z:{z}")

		#######################
		### Load Superslice ###
		#######################
		brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/superslice_{}.nii".format(z) #<---------- !!!
		brain = np.array(nib.load(brain_file).get_data(), copy=True)
		fly_idx_delete = 3 #(fly_095)
		brain = np.delete(brain, fly_idx_delete, axis=-1) #### DELETING FLY_095 ####

		# Get cluster responses for this slice
		for fly in fly_names:
			flies[fly].load_brain_slice()
			flies[fly].get_cluster_averages(cluster_model_labels_all[z,:], n_clusters)

		#################
		### Main Loop ###
		#################
		cluster_responses = []
		for cluster_num in range(n_clusters):
		    if cluster_num%100 == 0:
		        printlog(str(cluster_num))
		    ###############################################################
		    ### Build Y vector for a single supervoxel (with all flies) ###
		    ###############################################################
		    all_fly_neural = []
		    for fly in fly_names:
		        signal = flies[fly].cluster_signals[cluster_num,:]
		        all_fly_neural.extend(signal)
		    Y = np.asarray(all_fly_neural)

		    ###########################################
		    ### Build the X matrix for this cluster ###
		    ###########################################
		    # For each fly, this cluster could have originally come from a different z-depth
		    # Get correct original z-depth
		    Xs_new = []
		    for i, fly in enumerate(fly_names):
		        cluster_indicies = flies[fly].cluster_indicies[cluster_num]
		        z_map = flies[fly].z_correction[:,:,z].ravel()
		        original_z = int(np.median(z_map[cluster_indicies]))
		        Xs_new.append(X[original_z,i,:,:])
		    Xs_new = np.asarray(Xs_new)
		    X_cluster = np.reshape(np.moveaxis(Xs_new,0,1),(-1,30456))

		    ###################
		    ### Dot Product ###
		    ###################
		    cluster_response = np.dot(X_cluster,Y)
		    cluster_responses.append(cluster_response)
		cluster_responses = np.asarray(cluster_responses)

		######################
		### Save Responses ###
		######################
		save_file = F"/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210316_neural_weighted_behavior/jerk/responses_{z}"
		np.save(save_file, cluster_responses)
		brain = None
		Y = None

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))	 