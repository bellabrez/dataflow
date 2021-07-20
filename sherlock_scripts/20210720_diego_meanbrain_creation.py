import os
import sys
import json
import time
from time import sleep
import datetime
import numpy as np
import nibabel as nib
import nrrd
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
	main_dir = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210720_make_diego_meanbrain"#20210126_alignment_package"
	#raw_dir = os.path.join(main_dir, 'raw_anats')
	clean_dir = os.path.join(main_dir, 'clean_anats')
	#sharp_dir = os.path.join(main_dir, 'sharp_anats')
	resolution = (0.58, 0.58, 1)

	# #######################
	# ### Clean Anatomies ###
	# #######################
	# # Loop over each anatomy in "raw_anats" directory, and saved a cleaned version to "clean_anats" directory

	# anats = os.listdir(raw_dir)
	# print('found raw anats: {}'.format(anats))

	# if not os.path.exists(clean_dir):
	# 	os.mkdir(clean_dir)

	# print('*** Start Cleaning ***')
	# for anat in anats:
	# 	print('cleaning {}'.format(anat))
	# 	clean_anat(os.path.join(raw_dir, anat), clean_dir)
	# print('*** Finished Cleaning ***')

	# #########################
	# ### Sharpen Anatomies ###
	# #########################
	# # Loop over each anatomy in "clean_anats" directory, and saved a sharp version to "sharp_anats" directory
	# clean_anats = os.listdir(clean_dir)
	# print('found clean anats: {}'.format(clean_anats))

	# if not os.path.exists(sharp_dir):
	# 	os.mkdir(sharp_dir)

	# print('*** Start Sharpening ***')
	# for anat in clean_anats:
	# 	print('sharpening {}'.format(anat))
	# 	sharpen_anat(os.path.join(clean_dir, anat), sharp_dir)
	# print('*** Finished Sharpening ***')

	##############
	### AFFINE ###
	##############
	type_of_transform = 'Affine'

	###   Affine_0    ###
	moving_dir = clean_dir
	name_out = 'affine_0'
	name_fixed = '20201209_1_w_01_intcor_clean.nrrd'
	sharpen_output = False
	alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

	###   Affine_1    ###
	moving_dir = clean_dir
	name_out = 'affine_1'
	name_fixed = 'affine_0'
	sharpen_output = False
	alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

	##################
	### NON-LINEAR ###
	##################
	type_of_transform = 'SyN'

	###    SyN_0    ###
	moving_dir = clean_dir
	name_out = 'syn_0'
	name_fixed = 'affine_1'
	sharpen_output = False
	alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

	###    SyN_1    ###
	moving_dir = clean_dir
	name_out = 'syn_1'
	name_fixed = 'syn_0'
	sharpen_output = False
	alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

	###    SyN_2    ###
	moving_dir = clean_dir
	name_out = 'syn_2'
	name_fixed = 'syn_1'
	sharpen_output = True
	alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

	###    SyN_3    ###
	moving_dir = clean_dir
	name_out = 'syn_3'
	name_fixed = 'syn_2'
	sharpen_output = True
	alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

	###    SyN_4    ###
	moving_dir = clean_dir
	name_out = 'syn_4'
	name_fixed = 'syn_3'
	sharpen_output = True
	alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

	# ###    SyN_5    ###
	# moving_dir = sharp_dir
	# name_out = 'syn_5'
	# name_fixed = 'syn_4'
	# sharpen_output = False
	# alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

	# ###    SyN_6    ###
	# moving_dir = sharp_dir
	# name_out = 'syn_6'
	# name_fixed = 'syn_5'
	# sharpen_output = False
	# alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output)

def load_numpy_brain(in_file):
	if in_file.endswith('.nii'):
		brain = np.asarray(nib.load(in_file).get_data().squeeze(), dtype='float32')
	elif in_file.endswith('.nrrd'):
		brain = np.asarray(nrrd.read(in_file)[0].squeeze(), dtype='float32')
	else:
		print(f'Could not load {in_file}')
	return brain

def avg_brains(input_directory, save_directory, save_name):
	### Load Brains ###
	files = os.listdir(input_directory)
	#bigbrain = np.zeros((len(files), 1024, 512, 256), dtype='float32',order='F') #my brain size
	bigbrain = np.zeros((len(files), 1485, 772, 273), dtype='float32',order='F') # should add code to get dims
	for i, file in enumerate(files):
		print(F"loading {file}")
		bigbrain[i,...] = load_numpy_brain(os.path.join(input_directory, file))
		#bigbrain[i,...] = np.asarray(nib.load(os.path.join(input_directory, file)).get_data(), dtype='float32')

	### Avg ###
	meanbrain = np.mean(bigbrain, axis=0)

	### Save ###
	save_file = os.path.join(save_directory, save_name + '.nii')
	nib.Nifti1Image(meanbrain, np.eye(4)).to_filename(save_file)
	print(F"Saved {save_file}")

def align_anat(fixed_path, moving_path, save_dir, type_of_transform, resolution, mirror):
	### Load fixed brain
	fixed = load_numpy_brain(fixed_path)
	fixed = ants.from_numpy(fixed)
	fixed.set_spacing(resolution)

	### Load moving brain
	moving = load_numpy_brain(moving_path)
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
	brain = load_numpy_brain(in_file)

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
	brain = load_numpy_brain(in_file)

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


def alignment_iteration(main_dir, moving_dir, name_out, name_fixed, type_of_transform, resolution, sharpen_output):
	save_dir = os.path.join(main_dir, name_out)
	if not os.path.exists(save_dir):
		os.mkdir(save_dir)

	if name_fixed.endswith('.nrrd'):
		fixed_path = os.path.join(main_dir, name_fixed)
	else:
		fixed_path = os.path.join(main_dir, f'{name_fixed}.nii')

	print(f'*** Start {name_out} ***')
	anats = os.listdir(moving_dir)
	for anat in anats:
		moving_path = os.path.join(moving_dir, anat)
		for mirror in [False]: # <--------------------------------------------------------------- TRUE/FALSE
			t0 = time.time()
			align_anat(fixed_path, moving_path, save_dir, type_of_transform, resolution, mirror)
			print('{} {} done. Duration {}s'.format(type_of_transform, anat, time.time()-t0))
	print(f'*** Finished {name_out} ***')

	save_dir = os.path.join(main_dir, name_out)
	avg_brains(input_directory=save_dir, save_directory=main_dir, save_name=name_out)

	if sharpen_output:
		in_file = os.path.join(main_dir, f'{name_out}.nii')
		save_dir = main_dir
		sharpen_anat(in_file, save_dir)
	else:
		pass

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