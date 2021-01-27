import os
import sys
import json
from time import sleep
import datetime
import numpy as np
import nibabel as nib
import scipy
from skimage.filters import threshold_triangle as triangle
from sklearn.preprocessing import quantile_transform
from skimage.filters import unsharp_mask

def main():
	'''
	This code will take a population of individual anatomies,
	and build a mean-anatomy via affine and non-linear diffeomorphic registration
	Steps involved:
		1) Clean Individual Anatomies
			- Intensity-based masking
			- Removal of non-contiguous blobs
			- Quantile normalization of intensity histogram
		2) Sharpen Individual Anatomies
		3) Affine align sharpened anatomies to seed brain and average. This creates affine_0.
		4) Affine align sharpened anatomies to affine_0 and average. This creates affine_1.
		5) Non-linear align sharpened anatomies to affine_1 and average. This creates syn_0.
		6) Repeat step 5 for 2 additional iterations, aligning to the newly created syn_x.
	'''

	# main_directory must contain a directory called "raw", which contains the raw individual anatomies
	main_dir = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210126_alignment_package"
	seed_brain = ""

	##########################
	### 1) Clean Anatomies ###
	##########################
	# Loop over each anatomy in "raw_anats" directory, and saved a cleaned version to "clean_anats" directory
	raw_dir = os.path.join(main_dir, 'raw_anats')
	anats = os.listdir(raw_dir)
	print('found raw anats: {}'.format(anats))

	clean_dir = os.path.join(main_dir, 'clean_anats')
	if not os.path.exists(clean_dir):
		os.mkdir(clean_dir)

	print('*** Start Cleaning ***')
	for anat in anats:
		print('cleaning {}'.format(anat))
		clean_anat(os.path.join(raw_dir, anat), clean_dir)
	print('*** Finished Cleaning ***')

	############################
	### 2) Sharpen Anatomies ###
	############################
	# Loop over each anatomy in "clean_anats" directory, and saved a sharp version to "sharp_anats" directory
	clean_anats = os.listdir(clean_dir)
	print('found clean anats: {}'.format(clean_anats))

	sharp_dir = os.path.join(main_dir, 'sharp_anats')
	if not os.path.exists(sharp_dir):
		os.mkdir(sharp_dir)

	print('*** Start Sharpening ***')
	for anat in clean_anats:
		print('sharpening {}'.format(anat))
		sharpen_anat(os.path.join(clean_dir, anat), sharp_dir)
	print('*** Finished Sharpening ***')

	###################
	### 3) Affine_0 ###
	###################
	# Align all fly brains (and their mirrors) to a chosen seed brain

	################
	### Affine_1 ###
	################
	# Align all fly brains (and their mirrors) to affine_0_mean.nii

	################
	### SyN_Iter ###
	################
	# Align all fly brains (and their mirrors) to affine_1_mean.nii

def avg_brains(input_directory, save_directory, save_name):
	### Load Brains ###
	files = os.listdir(input_directory)
	bigbrain = np.zeros((len(files), 1024, 512, 256), dtype='float32',order='F')
	for i, file in enumerate(files):
		printlog(F"loading {file}")
		bigbrain[i,...] = np.asarray(nib.load(os.path.join(input_directory, file)).get_data(), dtype='float32')

	### Avg ###
	meanbrain = np.mean(bigbrain, axis=0)

	### Save ###
	save_file = os.path.join(save_directory, save_name + '.nii')
	nib.Nifti1Image(meanbrain, np.eye(4)).to_filename(save_file)
	printlog(F"Saved {save_file}")

def align_anat():
	pass

def clean_anat(in_file, save_dir):
	### Load brain ###
	#file = os.path.join(directory, 'stitched_brain_red_mean.nii') 
	brain = np.asarray(nib.load(in_file).get_data(), dtype='float32')

	### Blur brain and mask small values ###
	brain_copy = brain.copy().astype('float32')
	brain_copy = scipy.ndimage.filters.gaussian_filter(brain_copy, sigma=10)
	threshold = triangle(brain_copy)
	brain_copy[np.where(brain_copy < threshold/2)] = 0

	### Remove blobs outside contiguous brain ###
	labels, label_nb = scipy.ndimage.label(brain_copy)
	brain_label = np.bincount(labels.flatten())[1:].argmax()+1
	brain_copy = brain.copy().astype('float32')
	brain_copy[np.where(labels != brain_label)] = np.nan

	### Perform quantile normalization ###
	brain_out = quantile_transform(brain_copy.flatten().reshape(-1, 1), n_quantiles=500, random_state=0, copy=True)
	brain_out = brain_out.reshape(brain.shape)
	np.nan_to_num(brain_out, copy=False)

	### Save brain ###
	fname = in_file.split('/')[-1].split('.')[0]
	save_file = os.path.join(save_dir, f'{fname}_clean.nii')
	aff = np.eye(4)
	img = nib.Nifti1Image(brain_out, aff)
	img.to_filename(save_file)

def sharpen_anat(in_file, save_dir):
	### Load brain ###
	#file = os.path.join(directory, 'anat_red_clean.nii') 
	brain = np.asarray(nib.load(in_file).get_data(), dtype='float32')

	# renormalize to .3-.7
	a = .3
	b = .7
	brain_input = a + (brain)*(b-a)

	# sharpen
	brain_sharp = unsharp_mask(brain_input, radius=3, amount=7)

	# make background nan
	brain_copy = brain_sharp.copy()
	brain_copy[np.where(brain_input < .31)] = np.nan

	# renormalize via quantile
	brain_out = quantile_transform(brain_copy.flatten().reshape(-1, 1), n_quantiles=500, random_state=0, copy=True)
	brain_out = brain_out.reshape(brain.shape);
	np.nan_to_num(brain_out, copy=False);

	### Save brain ###
	fname = in_file.split('/')[-1].split('.')[0]
	save_file = os.path.join(save_dir, f'{fname}_sharp.nii')
	aff = np.eye(4)
	img = nib.Nifti1Image(brain_out, aff)
	img.to_filename(save_file)

if __name__ == '__main__':
	main()