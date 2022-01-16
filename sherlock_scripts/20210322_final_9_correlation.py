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

    logfile = args['logfile']
    save_directory = args['save_directory']
    z = args['z']
    behavior_to_corr = args['behavior_to_corr']


    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')
    printlog('{},{}'.format(behavior_to_corr, z))

    fly_names = ['fly_087', 'fly_089', 'fly_094', 'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_105']
    dataset_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset"
    expt_len = 1000*30*60
    resolution = 10
    high_res_timepoints = np.arange(0,expt_len,resolution) #0 to last time at subsample res

    #######################
    ### Load Superslice ###
    #######################
    brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/superslice_{}.nii".format(z) #<---------- !!!
    #RED!!!!:
    #brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/red/superslice_{}.nii".format(z) #<---------- !!!
    brain = np.array(nib.load(brain_file).get_data(), copy=True)
    fly_idx_delete = 3 #(fly_095)
    brain = np.delete(brain, fly_idx_delete, axis=-1) #### DELETING FLY_095 ####

    #####################
    ### Load Clusters ###
    #####################

    n_clusters = 2000
    #labels_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/final_9_cluster_labels_2000.npy'
    labels_file = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201129_super_slices/cluster_labels.npy'
    cluster_model_labels = np.load(labels_file)
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
        flies[fly].get_cluster_averages(cluster_model_labels, n_clusters)

    #####################
    ### Pool behavior ###
    #####################
    not_clipped_behaviors = ['Y', 'Z', 'Ya', 'Za']
    clipped_behaviors = ['Y_pos', 'Y_neg',
                         'Z_pos', 'Z_neg',
                         'Ya_pos', 'Ya_neg',
                         'Za_pos', 'Za_neg']
    all_behaviors = not_clipped_behaviors + clipped_behaviors

    pooled_behavior = {}
    for j, behavior in enumerate(all_behaviors):
        pooled_behavior[behavior] = []
        for i,fly in enumerate(flies):
            pooled_behavior[behavior].append(flies[fly].fictrac.fictrac[behavior])
        pooled_behavior[behavior] = np.asarray(pooled_behavior[behavior]).flatten()

    ###################
    ### Correlation ###
    ###################
    
    r_values = []
    p_values = []
    for cluster in range(n_clusters):
        pooled_activity = []
        for fly in flies:
            pooled_activity.append(flies[fly].cluster_signals[cluster])
        pooled_activity = np.asarray(pooled_activity).flatten()

        Y = pooled_activity
        X = pooled_behavior[behavior_to_corr]

        r, p = scipy.stats.pearsonr(X, Y)
        r_values.append(r)
        p_values.append(p)

        # CONFIRMED IDENTICAL ON 20210101
        # Calculate p-value a 2nd way for comparison
        # n = len(Y)
        # t = (r*np.sqrt(n-2))/(np.sqrt(1-r**2))
        # p_manual = scipy.stats.t.sf(abs(t), df=n-2)*2
        # p_values_t_test.append(p_manual)

        # if cluster%100 == 0:
        #     printlog(str(cluster))

    #####################
    ### Save Map Data ###
    #####################
    save_file = os.path.join(save_directory, 'rvalues_{}_z{}'.format(behavior_to_corr, z))
    np.save(save_file, np.asarray(r_values))

    save_file = os.path.join(save_directory, 'pvalues_{}_z{}'.format(behavior_to_corr, z))
    np.save(save_file, np.asarray(p_values))

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))