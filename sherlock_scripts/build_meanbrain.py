import time
import sys
import os
import re
import json
import datetime
import pyfiglet
import textwrap
import dataflow as flow

modules = 'gcc/6.3.0 python/3.6.1 py-numpy/1.14.3_py36 py-pandas/0.23.0_py36 viz py-scikit-learn/0.19.1_py36'

#########################
### Setup preferences ###
#########################

width = 120 # width of print log
nodes = 2 # 1 or 2
nice = True # true to lower priority of jobs. ie, other users jobs go first

flies = ['fly_087', 'fly_089', 'fly_092', 'fly_093', 'fly_094', 'fly_096',
         'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_102', 'fly_105', 'fly_106',
         'fly_110', 'fly_111']
#seed_fly = 'fly_091'
save_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain"
#flies = ['fly_' + str(x).zfill(3) for x in list(range(84,112))]

#####################
### Setup logging ###
#####################

logfile = './logs/' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')
sys.stderr = flow.Logger_stderr_sherlock(logfile)

###################
### Setup paths ###
###################

imports_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports/build_queue"
scripts_path = "/home/users/brezovec/projects/dataflow/sherlock_scripts"
com_path = "/home/users/brezovec/projects/dataflow/sherlock_scripts/com"
dataset_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset"

###################
### Print Title ###
###################

title = pyfiglet.figlet_format("Meanbrain", font="cyberlarge" ) #28 #shimrod
title_shifted = ('\n').join([' '*30+line for line in title.split('\n')][:-2])
printlog(title_shifted)
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog(F"{day_now+' | '+time_now:^{width}}")
printlog("")

################
### Affine_0 ###
################
# Align all fly brains (and their mirrors) to a chosen seed brain

# printlog(f"\n{'   Affine Iter   ':=^{width}}")
# job_ids = []
# fixed_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain/seed/seed_fly91_clean_20200803.nii"
# fixed_fly = 'fly_91_seed'
# type_of_transform = 'Affine'
# for fly in flies:
#     for mirror in [True, False]:
#         moving_path = os.path.join(dataset_path, fly, 'anat_0', 'moco', 'anat_red_clean.nii')
#         moving_fly = fly

#         args = {'logfile': logfile,
#                 'save_directory': save_directory,
#                 'fixed_path': fixed_path,
#                 'moving_path': moving_path,
#                 'fixed_fly': fixed_fly,
#                 'moving_fly': moving_fly,
#                 'type_of_transform': type_of_transform,
#                 'mirror': mirror}

#         script = 'align_anat.py'
#         job_id = flow.sbatch(jobname='align',
#                              script=os.path.join(scripts_path, script),
#                              modules=modules,
#                              args=args,
#                              logfile=logfile, time=4, mem=4, nice=nice, nodes=nodes) # 2 to 1
#         job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

################
### Affine_1 ###
################
# Align all fly brains (and their mirrors) to affine_0_mean.nii

# printlog(f"\n{'   Affine_1   ':=^{width}}")
# job_ids = []
# fixed_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain/affine_0_mean.nii"
# fixed_fly = 'affine_0_mean'
# type_of_transform = 'Affine'
# save_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain/affine_1"
# if not os.path.exists(save_directory):
#     os.mkdir(save_directory)

# for fly in flies:
#     for mirror in [True, False]:
#         moving_fly = fly
#         moving_path = os.path.join(dataset_path, fly, 'anat_0', 'moco', 'anat_red_clean.nii')

#         args = {'logfile': logfile,
#                 'save_directory': save_directory,
#                 'fixed_path': fixed_path,
#                 'moving_path': moving_path,
#                 'fixed_fly': fixed_fly,
#                 'moving_fly': moving_fly,
#                 'type_of_transform': type_of_transform,
#                 'mirror': mirror}

#         script = 'align_anat.py'
#         job_id = flow.sbatch(jobname='align',
#                              script=os.path.join(scripts_path, script),
#                              modules=modules,
#                              args=args,
#                              logfile=logfile, time=1, mem=2, nice=nice, nodes=nodes) # 2 to 1
#         job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

################
### SyN_Iter ###
################
# Align all fly brains (and their mirrors) to affine_1_mean.nii

# iterations = 1
# root_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200811_meanbrain"

# # if iter = 0, fixed = seed, 
# # if iter = 1, fixed = syn_0_mean
# # if iteration = 5, fixed = syn_4_mean, output dir = syn_5, savebrain = syn_5_mean

# for iteration in range(iterations):
#     printlog(f"\n{'   SyN Iteration ' + str(iteration+1) + '    ':=^{width}}")

#     if iteration == 0:
#         fixed_fly = "seed_syn_1_mean.nii"
#     else:
#         fixed_fly = "syn_{}_mean.nii".format(iteration-1) # use mean from previous iter round
#     fixed_path = os.path.join(root_directory, fixed_fly)

#     output_directory = os.path.join(root_directory, "syn_{}".format(iteration))
#     if not os.path.exists(output_directory):
#         os.mkdir(output_directory)

#     moving_resolution = (0.65, 0.65, 1)
#     fixed_resolution = (0.65, 0.65, 1)
#     mimic_resolution = (0.65, 0.65, 1)
#     flip_Z = False
#     type_of_transform = 'SyN'

#     job_ids = []
#     for fly in flies:
#         for flip_X in [True, False]:
#             moving_fly = fly
#             moving_path = os.path.join(dataset_path, fly, 'anat_0', 'moco', 'anat_red_clean_sharp.nii')

#             mimic_fly = fly
#             mimic_path = os.path.join(dataset_path, fly, 'anat_0', 'moco', 'anat_red_clean.nii')

#             args = {'logfile': logfile,
#                     'save_directory': output_directory,
#                     'fixed_path': fixed_path,
#                     'moving_path': moving_path,
#                     'fixed_fly': fixed_fly,
#                     'moving_fly': moving_fly,
#                     'type_of_transform': type_of_transform,
#                     'flip_X': flip_X,
#                     'flip_Z': flip_Z,
#                     'moving_resolution': moving_resolution,
#                     'fixed_resolution': fixed_resolution,
#                     'mimic_path': mimic_path,
#                     'mimic_fly': mimic_fly,
#                     'mimic_resolution': mimic_resolution}

#             script = 'align_anat.py'
#             job_id = flow.sbatch(jobname='align',
#                                  script=os.path.join(scripts_path, script),
#                                  modules=modules,
#                                  args=args,
#                                  logfile=logfile, time=8, mem=4, nice=nice, nodes=nodes) # 2 to 1
#             job_ids.append(job_id)

#     for job_id in job_ids:
#         flow.wait_for_job(job_id, logfile, com_path)

#     ######################
#     ### Make Meanbrain ###
#     ######################

#     save_directory = root_directory
#     input_directory = output_directory
#     save_name = "syn_{}_mean".format(iteration)

#     printlog(f"\n{'   LOOP   ':=^{width}}")
#     args = {'logfile': logfile,
#             'save_directory': save_directory,
#             'input_directory': input_directory,
#             'save_name': save_name}
#     script = 'avg_brains.py'
#     job_id = flow.sbatch(jobname='avgbrn',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=1, mem=4, nice=nice, nodes=nodes) # 2 to 1
#     flow.wait_for_job(job_id, logfile, com_path)

##########################
### Template alignment ###
##########################

res_JFRC = (0.62, 0.62, 0.62)
res_IBNWB = (0.64, 0.64, 1.41)
res_LUKE = (0.65, 0.65, 1)
res_DIEGO = (0.75, 0.75, 1.0)
res_KEVIN = (0.62,0.62,0.6)

printlog(f"\n{'   Template Alignment   ':=^{width}}")
moving_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates/seed_syn_1_mean_0810.nii"
moving_fly = "seed_syn_1_mean_0810"
moving_resolution = res_LUKE

fixed_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates/IBNWB.nii"
fixed_fly = 'IBNWB'
fixed_resolution = res_IBNWB

save_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates"
if not os.path.exists(save_directory):
    os.mkdir(save_directory)

type_of_transform = 'SyN'
flip_X = False
flip_Z = True

args = {'logfile': logfile,
        'save_directory': save_directory,
        'fixed_path': fixed_path,
        'moving_path': moving_path,
        'fixed_fly': fixed_fly,
        'moving_fly': moving_fly,
        'type_of_transform': type_of_transform,
        'flip_X': flip_X,
        'flip_Z': flip_Z,
        'moving_resolution': moving_resolution,
        'fixed_resolution': fixed_resolution}

script = 'align_anat.py'
job_id = flow.sbatch(jobname='align',
                     script=os.path.join(scripts_path, script),
                     modules=modules,
                     args=args,
                     logfile=logfile, time=8, mem=8, nice=nice, nodes=nodes) # 2 to 1

flow.wait_for_job(job_id, logfile, com_path)

#############
### SyN_from affine folder ###
#############
# Align all fly brains (and their mirrors) to affine_1_mean.nii

# printlog(f"\n{'   Affine_1   ':=^{width}}")
# job_ids = []
# fixed_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain/affine_1_mean.nii"
# fixed_fly = 'affine_1_mean'
# type_of_transform = 'SyN'
# save_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain/syn_0_from_affine"
# if not os.path.exists(save_directory):
#     os.mkdir(save_directory)


# moving_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain/affine_1"
# brain_files = os.listdir(moving_directory)

# for file in brain_files:
#     mirror=False
#     moving_fly = file
#     moving_path = os.path.join(moving_directory, file)

#     args = {'logfile': logfile,
#             'save_directory': save_directory,
#             'fixed_path': fixed_path,
#             'moving_path': moving_path,
#             'fixed_fly': fixed_fly,
#             'moving_fly': moving_fly,
#             'type_of_transform': type_of_transform,
#             'mirror': mirror}

#     script = 'align_anat.py'
#     job_id = flow.sbatch(jobname='align',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=8, mem=4, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

############
### Done ###
############

time.sleep(30) # to allow any final printing
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog("="*width)
printlog(F"{day_now+' | '+time_now:^{width}}")