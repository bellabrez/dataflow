import os
import sys
import numpy as np
import argparse
import subprocess
import json
import time
from scipy.interpolate import interp1d
import scipy
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow

def main(args):
	logfile = args['logfile']
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

	class Fictrac:
		def __init__ (self, fly_dir, timestamps):
			self.fictrac_raw = bbb.load_fictrac(os.path.join(fly_dir, 'fictrac'))
			self.timestamps = timestamps
		def make_interp_object(self, behavior):
			# Create camera timepoints
			fps=50
			camera_rate = 1/fps * 1000 # camera frame rate in ms
			expt_len = 1000*30*60
			x_original = np.arange(0,expt_len,camera_rate)

			# Smooth raw fictrac data
			fictrac_smoothed = scipy.signal.savgol_filter(np.asarray(self.fictrac_raw[behavior]),25,3)

			# Create interp object with camera timepoints
			fictrac_interp_object = interp1d(x_original, fictrac_smoothed, bounds_error = False)
			return fictrac_smoothed, fictrac_interp_object

		def pull_from_interp_object(self, interp_object, timepoints):
			new_interp = interp_object(timepoints)
			np.nan_to_num(new_interp, copy=False);
			return new_interp

		def interp_fictrac(self):
			behaviors = ['dRotLabY', 'dRotLabZ']; shorts = ['Y', 'Z']
			self.fictrac = {}

			for behavior, short in zip(behaviors, shorts):
				raw_smoothed, interp_object = self.make_interp_object(behavior)
				self.fictrac[short + 'i'] = interp_object
				self.fictrac[short] = raw_smoothed

		def make_walking_vector(self):
			self.fictrac['W'] = np.zeros(len(self.fictrac['Y']))
			YZ = np.sqrt(np.power(self.fictrac['Y']/np.std(self.fictrac['Y']),2),
				 np.power(self.fictrac['Z']/np.std(self.fictrac['Z']),2))
			self.fictrac['W'][np.where(YZ>.2)] = 1

			fps=50
			camera_rate = 1/fps * 1000 # camera frame rate in ms
			expt_len = 1000*30*60
			x_original = np.arange(0,expt_len,camera_rate)
			self.fictrac['Wi'] = interp1d(x_original, self.fictrac['W'], bounds_error = False, kind = 'nearest')

	def build_timeshifted_behavior_matrix(time_shifts, fly, z, behavior):
		# Get correct behavior interp obj
		if 'Z' in behavior: behavior_i = 'Zi'
		if 'Y' in behavior: behavior_i = 'Yi'
		if 'W' in behavior: behavior_i = 'Wi'

		interp_obj = flies[fly].fictrac.fictrac[behavior_i]

		behavior_shifts = []
		for shift in time_shifts:
			fictrac_interp = interp_obj(flies[fly].timestamps[:,z]+shift)
			fictrac_interp = np.nan_to_num(fictrac_interp)
			if 'pos' in behavior:
				fictrac_interp = np.clip(fictrac_interp, a_min=0, a_max=None)
			if 'neg' in behavior:
				fictrac_interp = np.clip(fictrac_interp, a_min=None, a_max=0)*-1
			#fictrac_interp[np.where(fictrac_interp == 0)] = np.nan
			behavior_shifts.append(fictrac_interp)

		return time_shifts, behavior_shifts

	def build_X (time_shifts, behaviors, z):
		all_fly_shifts = []
		for fly in fly_names:
			all_behavior_shifts = []
			for behavior in behaviors:
				time_shifts, behavior_shifts = build_timeshifted_behavior_matrix(time_shifts=time_shifts,
																				 fly=fly,
																				 z=z,
																				 behavior=behavior)
				all_behavior_shifts.append(np.asarray(behavior_shifts))
			all_behavior_shifts = np.asarray(all_behavior_shifts)
			all_behavior_shifts = np.reshape(all_behavior_shifts, (-1,3384))
			all_fly_shifts.append(all_behavior_shifts)
		X = np.asarray(all_fly_shifts)
	return X

	###################
	### Build Flies ###
	###################
	flies = {}
	for i, fly in enumerate(fly_names):
		flies[fly] = Fly(fly_name=fly, fly_idx=i)
		flies[fly].load_timestamps()
		flies[fly].load_fictrac()
		flies[fly].fictrac.interp_fictrac()
		flies[fly].fictrac.make_walking_vector()

	time_shifts = list(range(-5000,5000,20)) # in ms
	behaviors = ['Y_pos', 'Z_pos', 'Z_neg', 'W']

	############################################
	### Build the complete X behavior matrix ###
	############################################
	Xs = []
	for z in range(49):
		printlog(z)
		X = build_X(time_shifts, behaviors, z)
		Xs.append(X)

	######################
	### Save Responses ###
	######################
	save_file = F"/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210316_neural_weighted_behavior/master_X"
	np.save(save_file, np.asarray(Xs))

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))	 