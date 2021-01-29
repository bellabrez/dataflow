import os
import sys
import json
import time
from time import sleep
import datetime
import numpy as np
import nibabel as nib
import scipy
import warnings
from contextlib import contextmanager
from skimage.filters import threshold_triangle as triangle
from sklearn.preprocessing import quantile_transform
from skimage.filters import unsharp_mask

sys.path.insert(0, '/home/users/brezovec/.local/lib/python3.6/site-packages/lib/python/')
import ants

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
		3) Affine align clean anatomies to seed brain and average. This creates affine_0.
		4) Affine align clean anatomies to affine_0 and average. This creates affine_1.
		5) Non-linear align sharpened anatomies to affine_1 and average. This creates syn_0.
		6) Repeat step 5 for 2 additional iterations, aligning to the newly created syn_x.
	'''

	# main_directory must contain a directory called "raw", which contains the raw individual anatomies
	main_dir = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210126_alignment_package"
	raw_dir = os.path.join(main_dir, 'raw_anats')
	clean_dir = os.path.join(main_dir, 'clean_anats')
	sharp_dir = os.path.join(main_dir, 'sharp_anats')

	##########################
	### 1) Clean Anatomies ###
	##########################
	# Loop over each anatomy in "raw_anats" directory, and saved a cleaned version to "clean_anats" directory

	anats = os.listdir(raw_dir)
	print('found raw anats: {}'.format(anats))

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
	save_dir = os.path.join(main_dir, 'affine_0')
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)

	fixed_path = os.path.join(main_dir, 'seed', 'seed_fly91_clean_20200803.nii')
	resolution = (0.65, 0.65, 1)
	type_of_transform = 'Affine'

	print('*** Start Affine_0 ***')
	anats = os.listdir(clean_dir)
	for anat in anats:
		moving_path = os.path.join(clean_dir, anat)
		for mirror in [True, False]:
			t0 = time.time()
			align_anat(fixed_path, moving_path, save_dir, type_of_transform, resolution, mirror)
			print('Affine {} done. Duration {}s'.format(anat, time.time()-t0))
	print('*** Finished Affine_0 ***')

	save_dir = os.path.join(main_dir, 'affine_0')
	avg_brains(input_directory=save_dir, save_directory=main_dir, save_name='affine_0')

	###################
	### 4) Affine_1 ###
	###################
	# Align all fly brains (and their mirrors) to affine_0_mean.nii
	save_dir = os.path.join(main_dir, 'affine_1')
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)

	fixed_path = os.path.join(main_dir, 'affine_0.nii')
	resolution = (0.65, 0.65, 1)
	type_of_transform = 'Affine'

	print('*** Start Affine_1 ***')
	anats = os.listdir(clean_dir)
	for anat in anats:
		moving_path = os.path.join(clean_dir, anat)
		for mirror in [True, False]:
			t0 = time.time()
			align_anat(fixed_path, moving_path, save_dir, type_of_transform, resolution, mirror)
			print('Affine {} done. Duration {}s'.format(anat, time.time()-t0))
	print('*** Finished Affine_1 ***')

	save_dir = os.path.join(main_dir, 'affine_1')
	avg_brains(input_directory=save_dir, save_directory=main_dir, save_name='affine_1')

	### sharpen affine_1
	in_file = os.path.join(main_dir, 'affine_1.nii')
	save_dir = main_dir
	sharpen_anat(in_file, save_dir)

	################
	### SyN_Iter ###
	################
	# Align all fly brains (and their mirrors) to affine_1_sharp.nii
	save_dir = os.path.join(main_dir, 'syn_0')
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)

	fixed_path = os.path.join(main_dir, 'affine_1_sharp.nii')
	resolution = (0.65, 0.65, 1)
	type_of_transform = 'SyN'

	print('*** Start SyN_0 ***')
	anats = os.listdir(sharp_dir)
	for anat in anats:
		moving_path = os.path.join(sharp_dir, anat)
		for mirror in [True, False]:
			t0 = time.time()
			align_anat(fixed_path, moving_path, save_dir, type_of_transform, resolution, mirror)
			print('SyN {} done. Duration {}s'.format(anat, time.time()-t0))
	print('*** Finished SyN_0 ***')

	save_dir = os.path.join(main_dir, 'syn_0')
	avg_brains(input_directory=save_dir, save_directory=main_dir, save_name='syn_0')

	### sharpen
	in_file = os.path.join(main_dir, 'syn_0.nii')
	save_dir = main_dir
	sharpen_anat(in_file, save_dir)

def avg_brains(input_directory, save_directory, save_name):
	### Load Brains ###
	files = os.listdir(input_directory)
	bigbrain = np.zeros((len(files), 1024, 512, 256), dtype='float32',order='F')
	for i, file in enumerate(files):
		print(F"loading {file}")
		bigbrain[i,...] = np.asarray(nib.load(os.path.join(input_directory, file)).get_data(), dtype='float32')

	### Avg ###
	meanbrain = np.mean(bigbrain, axis=0)

	### Save ###
	save_file = os.path.join(save_directory, save_name + '.nii')
	nib.Nifti1Image(meanbrain, np.eye(4)).to_filename(save_file)
	print(F"Saved {save_file}")

def align_anat(fixed_path, moving_path, save_dir, type_of_transform, resolution, mirror):
	### Load fixed brain
	fixed = np.asarray(nib.load(fixed_path).get_data().squeeze(), dtype='float32')
	fixed = ants.from_numpy(fixed)
	fixed.set_spacing(resolution)

	### Load moving brain
	moving = np.asarray(nib.load(moving_path).get_data().squeeze(), dtype='float32')
	if mirror:
		moving = moving[::-1,:,:]
	moving = ants.from_numpy(moving)
	moving.set_spacing(resolution)

	### Align
	with stderr_redirected(): # to prevent itk gaussian error infinite printing
		moco = ants.registration(fixed, moving, type_of_transform=type_of_transform)

	### Save
	fixed_fly = fixed_path.split('/')[-1].split('.')[0]
	moving_fly = moving_path.split('/')[-1].split('.')[0]
	if mirror:
		save_file = os.path.join(save_dir, moving_fly + '_m' + '-to-' + fixed_fly)
	else:
		save_file = os.path.join(save_dir, moving_fly + '-to-' + fixed_fly)
	save_file += '.nii'
	nib.Nifti1Image(moco['warpedmovout'].numpy(), np.eye(4)).to_filename(save_file)

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

@contextmanager
def stderr_redirected(to=os.devnull):

	fd = sys.stderr.fileno()

	def _redirect_stderr(to):
		sys.stderr.close() # + implicit flush()
		os.dup2(to.fileno(), fd) # fd writes to 'to' file
		sys.stderr = os.fdopen(fd, 'w') # Python writes to fd

	with os.fdopen(os.dup(fd), 'w') as old_stderr:
		with open(to, 'w') as file:
			_redirect_stderr(to=file)
		try:
			yield # allow code to be run with the redirected stdout
		finally:
			_redirect_stderr(to=old_stderr) # restore stdout.
											# buffering and flags such as
											# CLOEXEC may be different

if __name__ == '__main__':
	main()