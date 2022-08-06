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

	### load synapses
	file = os.path.join(connectome_dir, 'hemibrain_all_neurons_synapses_polypre_centrifugal_synapses.pickle')
	file = open(file, 'rb')
	synapses = pickle.load(file)
	printlog('loaded synapses')

	cell_ids = np.unique(synapses['bodyid'])


	### loop over cells
	synpervox = np.empty((24691,101,84,29),dtype='uint16')
	for j, cell in enumerate(cell_ids):
		if j%1000 == 0:
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
		synpervox[j,...] = DN_crop

	save_file = os.path.join(connectome_dir, 'synpervox')
	np.save(save_file, synpervox)
	printlog('DONE; SAVED')

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))