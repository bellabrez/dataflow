import os
import sys
import numpy as np
import argparse
import subprocess
import json
import time
import scipy
import nibabel as nib
import bigbadbrain as bbb
import dataflow as flow
import pickle

def main(args):

	logfile = args['logfile']
	printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')
	connectome_dir = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20220624_supervoxels_in_FDA'
	# hemibrain bounding box
	start = {'x': 46, 'y': 5, 'z': 5}
	stop = {'x': 147, 'y': 89, 'z': 34}

	### load behavior scores ###
	unique_crop = np.load(os.path.join(connectome_dir, 'unique_glm_in_hemibrain.npy'))
	printlog('loaded unique_crop')

	### load synapses
	file = os.path.join(connectome_dir, 'hemibrain_all_neurons_synapses_polypre_centrifugal_synapses.pickle')
	file = open(file, 'rb')
	synapses = pickle.load(file)
	printlog('loaded synapses')

	cell_ids = np.unique(synapses['bodyid'])

	### prep beh
	behavior = []
	for beh in [0,1,2]:
		unique_crop_thresh = unique_crop[...,beh].copy()
		unique_crop_thresh[unique_crop[...,beh]>=.01] =  1
		unique_crop_thresh[unique_crop[...,beh]<.01] =  np.nan
		behavior.append(unique_crop_thresh==1)
	printlog('preped beh')

	### loop over cells and get dice score
	all_dice = []
	for j, cell in enumerate(cell_ids[:10]):
		if j%10 == 0:
			printlog(f'j: {j}')
		idx = list(np.where(synapses['bodyid']==cell)[0])
		xs = synapses['x'][idx]
		ys = synapses['y'][idx]
		zs = synapses['z'][idx]
		DN = np.histogramdd((xs*.38,ys*.38,zs*.38),
				bins=(np.arange(0,242*2.6,2.6), np.arange(0,113*2.6,2.6), np.arange(0,37*5,5)))[0]
		DN_crop = DN[start['x']:stop['x'],
						  start['y']:stop['y'],
						  start['z']:stop['z']]
		DN_crop[DN_crop>0] = 1
		DN_crop[DN_crop == 0] = np.nan
		arr1 = DN_crop>0

		cell_dice = []
		for beh in [0,1,2]:
			arr2 = behavior[beh]
			arr3 = np.logical_and(arr1, arr2)
			dice = 2*np.sum(arr3)/(np.sum(arr1)+np.sum(arr2))
			cell_dice.append(dice)
		all_dice.append(cell_dice)

	data_to_save = np.asarray(all_dice)
	save_file = os.path.join(connectome_dir, 'all_neuron_dice')
	np.save(save_file, data_to_save)
	printlog('DONE; SAVED')

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))