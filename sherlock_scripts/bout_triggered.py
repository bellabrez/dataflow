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
	z = args['z']
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
			return fictrac_interp_object

		def pull_from_interp_object(self, interp_object, timepoints):
			new_interp = interp_object(timepoints)
			np.nan_to_num(new_interp, copy=False);
			return new_interp

		def interp_fictrac(self, z):
			behaviors = ['dRotLabY', 'dRotLabZ']; shorts = ['Y', 'Z']
			self.fictrac = {}

			for behavior, short in zip(behaviors, shorts):
				interp_object = self.make_interp_object(behavior)
				self.fictrac[short + 'i'] = interp_object

				### Velocity ###
				low_res_behavior = self.pull_from_interp_object(interp_object, self.timestamps[:,z])
				self.fictrac[short] = low_res_behavior#/np.std(low_res_behavior)

				### Clipped Velocities ###
				self.fictrac[short + '_pos'] = np.clip(self.fictrac[short], a_min=0, a_max=None)
				self.fictrac[short + '_neg'] = np.clip(self.fictrac[short], a_min=None, a_max=0)*-1

				### Strongly Clipped Velocities ###
				# excludes points even close to 0
				#self.fictrac[short + '_pos_very'] = np.clip(self.fictrac[short], a_min=0.3, a_max=None)
				#self.fictrac[short + '_neg_very'] = np.clip(self.fictrac[short], a_min=None, a_max=-0.3)*-1

				### Acceleration ###
				high_res_behavior = self.pull_from_interp_object(interp_object, high_res_timepoints)
				self.fictrac[short + 'h'] = high_res_behavior/np.std(high_res_behavior)

				accel = scipy.signal.savgol_filter(np.diff(high_res_behavior),25,3)
				accel = np.append(accel, 0)
				interp_object = interp1d(high_res_timepoints, accel, bounds_error = False)
				acl = interp_object(self.timestamps[:,z])
				acl[-1] = 0
				self.fictrac[short + 'a'] = acl#/np.std(acl)

				### Clipped Acceleration ###
				self.fictrac[short + 'a' + '_pos'] = np.clip(self.fictrac[short + 'a'], a_min=0, a_max=None)
				self.fictrac[short + 'a' + '_neg'] = np.clip(self.fictrac[short + 'a'], a_min=None, a_max=0)*-1

			self.fictrac['YZ'] = np.sqrt(np.power(self.fictrac['Y'],2), np.power(self.fictrac['Z'],2))
			self.fictrac['YZh'] = np.sqrt(np.power(self.fictrac['Yh'],2), np.power(self.fictrac['Zh'],2))

	def find_bouts(fly):
		expt_len = 1000*30*60
		resolution = 10
		high_res_timepoints = np.arange(0,expt_len,resolution) #0 to last time at subsample res

		behavior = 'Yh'

		B_THRESHOLD = np.std(flies[fly].fictrac.fictrac[behavior])/4
		ALIVE_TIME = 1000 # in ms
		DEAD_TIME = 1000 # in ms

		state = 'quiescent'
		up_streak = 0
		down_streak = 0
		BOUTS = []
		ALIVE_TIME = int(ALIVE_TIME/resolution)
		DEAD_TIME = int(DEAD_TIME/resolution)

		for i in range(len(flies[fly].fictrac.fictrac[behavior])):
			# If high behavior, reset down_streak, and add 1 to up_streak
			if flies[fly].fictrac.fictrac[behavior][i] > B_THRESHOLD:
				down_streak = 0
				up_streak += 1
			else:
				up_streak = 0
				down_streak += 1

			if state == 'quiescent':
				if up_streak >= ALIVE_TIME:
					state = 'moving'
					BOUTS.append({'start': i-ALIVE_TIME})
			elif state == 'moving':
				if down_streak >= DEAD_TIME:
					state = 'quiescent'
					BOUTS[-1]['end'] = i-DEAD_TIME
		BOUTS = [bout for bout in BOUTS if 'end' in bout]
		#print('Found {} bouts'.format(len(BOUTS)))

		### Clean Start Bouts
		# remove bouts that have behavior too close *before* them
		before = 1000 # in ms
		before = int(before/10)
		start_bouts=[bout for bout in BOUTS if np.mean(np.abs(flies[fly].fictrac.fictrac[behavior][bout['start']-before:bout['start']])) < .2]
		#print('Remaining start_bouts post-cleaning: {}'.format(np.shape(start_bouts)[0]))

		### Clean Stop Bouts
		# remove bouts that have behavior too close *after* them
		before = 1000 # in ms
		before = int(before/10)
		stop_bouts=[bout for bout in BOUTS if np.mean(np.abs(flies[fly].fictrac.fictrac[behavior][bout['end']:bout['end']+before])) < .2]
		#print('Remaining stop_bouts bouts post-cleaning: {}'.format(np.shape(stop_bouts)[0]))
		return start_bouts, stop_bouts

	def bout_triggered(fly, neural_data, all_bouts, bout_type, original_z):
		if bout_type == 'start_bouts':
			align_to = 'start'
		elif bout_type == 'stop_bouts':
			align_to = 'end'
		before = 3000 #in ms
		after = 3000 # in ms
		jump = flies[fly].timestamps[1,0]-flies[fly].timestamps[0,0]
		num_neural_points = int(before/jump)

		before = int(before/10) # now everything is in units of 10ms
		after = int(after/10)
		bins = bbb.create_bins(10,before*10,after*10)[:-1]

		xss = []; yss = []
		for i in range(len(all_bouts[bout_type])):
			nearest = np.searchsorted(flies[fly].timestamps[:,original_z]/10, all_bouts[bout_type][i][align_to])
			offset = (flies[fly].timestamps[nearest,original_z]/10 - all_bouts[bout_type][i][align_to])*10
			xs = np.arange(offset-num_neural_points*jump,offset+num_neural_points*jump,jump)
			ys = neural_data[nearest-num_neural_points:nearest+num_neural_points]
			if len(ys) == 10:
				xss.append(xs); yss.append(ys)
		xss = np.asarray(xss); yss = np.asarray(yss)
		
		sum_bouts = [flies[fly].fictrac.fictrac['Yh'][bout[align_to]-before:bout[align_to]+after] for bout in all_bouts[bout_type]][1:-1]
		sum_bouts = np.asarray(sum_bouts)
		#avg_bout = np.mean(sum_bouts,axis=0)
		
		return xss, yss, sum_bouts

	#######################
	### Load Superslice ###
	#######################
	brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/superslice_{}.nii".format(z) #<---------- !!!
	brain = np.array(nib.load(brain_file).get_data(), copy=True)
	fly_idx_delete = 3 #(fly_095)
	brain = np.delete(brain, fly_idx_delete, axis=-1) #### DELETING FLY_095 ####

	#####################
	### Load Clusters ###
	#####################
	n_clusters = 2000
	labels_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/final_9_cluster_labels_2000.npy'
	cluster_model_labels = np.load(labels_file) #z,t
	cluster_model_labels = cluster_model_labels[z,:]

	###################
	### Build Flies ###
	###################
	flies = {}
	for i, fly in enumerate(fly_names):
		flies[fly] = Fly(fly_name=fly, fly_idx=i)
		flies[fly].load_timestamps()
		flies[fly].load_fictrac()
		flies[fly].fictrac.interp_fictrac(z)
		flies[fly].load_brain_slice()
		flies[fly].load_z_depth_correction()
		flies[fly].get_cluster_averages(cluster_model_labels, n_clusters)

	#################
	### Main Loop ###
	#################
	xss_master = []; yss_master = []; sum_bouts_master = []
	for cluster_num in range(n_clusters):
		if cluster_num%100 == 0:
			printlog(str(cluster_num))

		# loop over flies
		bout_type = 'start_bouts'
		pooled_bouts = {'xss': np.empty((0,10)), 'yss': np.empty((0,10)), 'sum_bouts': np.empty((0,600))}
		for fly in fly_names:
			# Get bout times
			start_bouts, stop_bouts = find_bouts(fly)
			all_bouts = {'start_bouts': start_bouts, 'stop_bouts': stop_bouts}
			neural_data = flies[fly].cluster_signals[cluster_num, :]

			# Get original_Z
			cluster_indicies = flies[fly].cluster_indicies[cluster_num]
			z_map = flies[fly].z_correction[:,:,z].ravel()
			original_z = int(np.median(z_map[cluster_indicies]))

			# Get bout triggered neural vectors
			xss, yss, sum_bouts = bout_triggered(fly, neural_data, all_bouts, bout_type, original_z)

			# Collect output from all flies
			pooled_bouts['xss'] = np.vstack((pooled_bouts['xss'], xss))
			pooled_bouts['yss'] = np.vstack((pooled_bouts['yss'], yss))
			pooled_bouts['sum_bouts'] = np.vstack((pooled_bouts['sum_bouts'], sum_bouts))
		# Collect output from all supervoxels
		xss_master.append(pooled_bouts['xss'])
		yss_master.append(pooled_bouts['yss'])
		
		#only need to save the behavior traces once. don't waste memory on 2000 duplicates
		if cluster_num == 0:
			sum_bouts_master.append(pooled_bouts['sum_bouts'])
	xss_master = np.asarray(xss_master)
	yss_master = np.asarray(yss_master)
	sum_bouts_master = np.asarray(sum_bouts_master)

	#############
	### Save  ###
	#############
	save_file = F"/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210111_bout_triggered/xss_{z}"
	np.save(save_file, xss_master)
	save_file = F"/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210111_bout_triggered/yss_{z}"
	np.save(save_file, yss_master)
	save_file = F"/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210111_bout_triggered/behavior_{z}"
	np.save(save_file, sum_bouts_master)

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))	 