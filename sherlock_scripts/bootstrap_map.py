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
    save_directory = args['save_directory']
    z = args['z']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    fly_names = ['fly_087', 'fly_089', 'fly_094', 'fly_095', 'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_105']
    dataset_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset"
    expt_len = 1000*30*60
    resolution = 10
    high_res_timepoints = np.arange(0,expt_len,resolution) #0 to last time at subsample res

    def create_clusters(brain, n_clusters):
        t0 = time.time()
        clustering_dir = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201110_analysis_superfly_supervoxels"
        super_to_cluster = brain.reshape(-1, 33840)
        connectivity = grid_to_graph(256,128)
        cluster_model = AgglomerativeClustering(n_clusters=n_clusters,
                                        memory=clustering_dir,
                                        linkage='ward',
                                        connectivity=connectivity)
        cluster_model.fit(super_to_cluster)
        return cluster_model

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
        def get_cluster_averages (self, cluster_model, n_clusters):
            neural_data = self.brain.reshape(-1, 3384)
            signals = []
            self.cluster_indicies = []
            for cluster_num in range(n_clusters):
                cluster_indicies = np.where(cluster_model.labels_==cluster_num)[0]
                mean_signal = np.mean(neural_data[cluster_indicies,:], axis=0)
                signals.append(mean_signal)
                self.cluster_indicies.append(cluster_indicies) # store for later
            self.cluster_signals=np.asarray(signals)
        def make_corr_map (self, n_clusters, cluster_model, behavior):
            corrs = []
            # remove zeros from correlation
            behavior_vector = flies[fly].fictrac.fictrac[behavior]
            non_zero_entries = np.where(behavior_vector != 0)[0]
            for i in range(n_clusters):
                cluster_indicies = np.where(cluster_model.labels_==i)[0]
                if len(cluster_indicies) > 2000:
                    corrs.append(0)
                else:
                    corrs.append(scipy.stats.pearsonr(behavior_vector[non_zero_entries],
                                                      self.cluster_signals[i,non_zero_entries])[0])
            colored_by_betas = np.zeros(256*128)
            for cluster_num in range(n_clusters):
                cluster_indicies = np.where(cluster_model.labels_==cluster_num)[0]
                colored_by_betas[cluster_indicies] = corrs[cluster_num]
            colored_by_betas = colored_by_betas.reshape(256,128)
            self.maps[behavior] = colored_by_betas
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

    #######################
    ### Load Superslice ###
    #######################
    brain_file = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201110_analysis_superfly_supervoxels/superslice_{}.nii".format(z)
    brain = np.array(nib.load(brain_file).get_data(), copy=True)

    #####################
    ### Make Clusters ###
    #####################
    n_clusters = 2000
    cluster_model = create_clusters(brain, n_clusters)

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
        flies[fly].get_cluster_averages(cluster_model, n_clusters)

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

    ### Correct behavior stddev as a pooled group
    stds = {}
    for j, behavior in enumerate(not_clipped_behaviors):
        stds[behavior] = np.std(pooled_behavior[behavior])

    for j, behavior in enumerate(all_behaviors):
        std_key = behavior.split('_')[0] # grab not split key
        for i,fly in enumerate(flies):
            flies[fly].fictrac.fictrac[behavior] = flies[fly].fictrac.fictrac[behavior]/stds[std_key]
        pooled_behavior[behavior] = pooled_behavior[behavior]/stds[std_key]

    #############################
    ### Bootstrap Comparisons ###
    #############################
    r_diffs = []
    sigs = []
    for cluster in range(n_clusters):
        t0=time.time()

        pooled_activity = []
        for fly in flies:
            pooled_activity.append(flies[fly].cluster_signals[cluster])
        pooled_activity = np.asarray(pooled_activity).flatten()

        Y_var = pooled_activity
        X_var_a = pooled_behavior['Z_neg']
        X_var_b = pooled_behavior['Z_pos']

        rs = []
        num_reps=1000
        for _ in range(num_reps):
            idx = np.random.choice(len(Y_var), len(Y_var))
            a=scipy.stats.pearsonr(X_var_a[idx], Y_var[idx])[0]
            b=scipy.stats.pearsonr(X_var_b[idx], Y_var[idx])[0]
            rs.append(a-b)

        r_diff = np.mean(rs) # get mean difference
        #Get p-value (see if zero is within the 95% confidence interval)
        zero_idx = np.searchsorted(np.sort(rs), 0)

        r_diffs.append(r_diff)
        sigs.append(zero_idx)
        if cluster%10 == 0:
            printlog(cluster)

    #####################
    ### Save Map Data ###
    #####################
    save_file = os.path.join(save_directory, 'rot_neg_pos_rdiff_z{}'.format(z))
    np.save(save_file, np.asarray(r_diffs))
    save_file = os.path.join(save_directory, 'rot_neg_pos_sig_z{}'.format(z))
    np.save(save_file, np.asarray(sigs))
    #img = nib.Nifti1Image(brain, np.eye(4)).to_filename(save_file)
    # printlog("brain save duration: ({})".format(time.time()-t0))



if __name__ == '__main__':
    main(json.loads(sys.argv[1]))