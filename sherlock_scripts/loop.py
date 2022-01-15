import time
import sys
import os
import re
import json
import datetime
import pyfiglet
import textwrap
import dataflow as flow

#modules = 'gcc/6.3.0 python/3.6.1 py-numpy/1.14.3_py36 py-pandas/0.23.0_py36 viz py-scikit-learn/0.19.1_py36'
#modules = 'py-numpy/1.14.3_py36 viz py-pandas/0.23.0_py36' #using until 20210103
#modules = 'py-numpy/1.18.1_py36 viz py-pandas/0.23.0_py36' #newer numpy 20210123 due to pca error
modules = 'python/3.6.1'
#modules = 'py-numpy/1.14.3_py36 viz py-matplotlib/2.2.2_py36 py-scipy/1.1.0_py36 py-scipystack/1.0_py36 py-pandas/0.23.0_py36'

#########################
### Setup preferences ###
#########################

width = 120 # width of print log
nodes = 2 # 1 or 2
nice = True # true to lower priority of jobs. ie, other users jobs go first

#flies = ['fly_084', 'fly_088', 'fly_091', 'fly_108']
#flies = ['fly_089', 'fly_094', 'fly_100']

#fly = 'fly_089'
# flies = ['fly_086', 'fly_087', 'fly_089', 'fly_092', 'fly_093', 'fly_094', 'fly_095', 'fly_096',
#          'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_103', 'fly_104', 'fly_105', 'fly_106',
#          'fly_107', 'fly_109', 'fly_110', 'fly_111']


# flies = ['fly_087', 'fly_089', 'fly_092', 'fly_093', 'fly_094', 'fly_096',
#          'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_105',
#          'fly_106', 'fly_110', 'fly_111']


# flies = ['fly_089', 'fly_092', 'fly_093', 'fly_094', 'fly_096',
#          'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_105',
#          'fly_106', 'fly_110', 'fly_111']

#flies = ['fly_086', 'fly_095', 'fly_103', 'fly_104', 'fly_107']

#flies = ['fly_087', 'fly_089', 'fly_094', 'fly_095', 'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_105']
#flies = ['fly_087', 'fly_089', 'fly_095', 'fly_097', 'fly_098', 'fly_099', 'fly_100', 'fly_101', 'fly_105']

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

title = pyfiglet.figlet_format("Loop", font="cyberlarge" ) #28 #shimrod
title_shifted = ('\n').join([' '*44+line for line in title.split('\n')][:-2])
printlog(title_shifted)
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog(F"{day_now+' | '+time_now:^{width}}")
printlog("")

###################
### LOOP SCRIPT ###
###################

#########################################
### NEURAL WEIGHTED BEHAVIOR - MAKE X ###
#########################################
job_ids = []
args = {'logfile': logfile}
script = 'create_behavior_X_matrix_acceleration.py'
job_id = flow.sbatch(jobname='neuwebeh',
                     script=os.path.join(scripts_path, script),
                     modules=modules,
                     args=args,
                     logfile=logfile, time=12, mem=12, nice=nice, nodes=nodes) # 2 to 1
job_ids.append(job_id)
for job_id in job_ids:
    flow.wait_for_job(job_id, logfile, com_path)

# printlog(f"\n{'   GLM - superfly reconstructed   ':=^{width}}")
# job_ids = []
# for num_pcs in [1, 10, 30, 50, 100, 500, 1000, 10000, 26840]:
#     args = {'logfile': logfile,
#             'num_pcs': num_pcs}
#     script = 'instantaneous_glm_unique_reconstructed.py'
#     job_id = flow.sbatch(jobname='glmsuper',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=6, mem=12, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# printlog(f"\n{'   GLM   ':=^{width}}")
# job_ids = []
# #[1, 10, 30, 50, 100, 500, 1000, 10000, 26840]
# #for num_pcs in [100]:
# args = {'logfile': logfile}
# script = 'instantaneous_glm_unique_state_subtraction.py'
# job_id = flow.sbatch(jobname='glm',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=24, mem=8, nice=nice, nodes=nodes) # 2 to 1
# job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# printlog(f"\n{'   CLUSTERING   ':=^{width}}")
# job_ids = []
# args = {'logfile': logfile}
# script = 'build_final_9_pooled_brain_for_pca.py'
# #script = 'final_9_depth_correct_clustering.py'
# job_id = flow.sbatch(jobname='cluster',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=24, mem=22, nice=nice, nodes=nodes) # 2 to 1
# job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

###########
### PCA ###
###########

# printlog(f"\n{'   PCA   ':=^{width}}")
# job_ids = []
# for fly_idx in range(9):
#     args = {'logfile': logfile, 'fly_idx': fly_idx}
#     script = 'pca_of_final_9.py'
#     job_id = flow.sbatch(jobname='pca',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=12, mem=12, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# printlog(f"\n{'   PCA   ':=^{width}}")
# X_type = 'five_fly'
# job_ids = []
# args = {'logfile': logfile, 'X_type': X_type}
# script = 'pca_of_final_9.py'
# job_id = flow.sbatch(jobname='pca',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=24, mem=23, nice=nice, nodes=nodes) # 2 to 1
# job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ##########################
# ### BUILD POOLED BRAIN ###
# ##########################

# printlog(f"\n{'   BUILD POOLED BRAIN   ':=^{width}}")
# job_ids = []
# args = {'logfile': logfile}
# script = 'build_final_9_pooled_brain.py'
# job_id = flow.sbatch(jobname='bdlbrn',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=2, mem=23, nice=nice, nodes=nodes) # 2 to 1
# job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ######################
# ### BOUT TRIGGERED ###
# ######################

# printlog(f"\n{'   Bout Triggered   ':=^{width}}")
# job_ids = []
# for z in range(49):
#     args = {'logfile': logfile,
#             'z': z}
#     script = 'bout_triggered.py'
#     job_id = flow.sbatch(jobname='bouts',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=2, mem=4, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ############
# ### UMAP ###
# ############

# printlog(f"\n{'   UMAP   ':=^{width}}")
# job_ids = []
# args = {'logfile': logfile}
# script = 'umap_.py'
# job_id = flow.sbatch(jobname='umap',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=96, mem=23, nice=nice, nodes=nodes) # 2 to 1
# job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ###################
# ### CORRELATION ###
# ###################

# printlog(f"\n{'   CORRELATIONS   ':=^{width}}")

# behaviors = ['Y_pos', 'Z_pos', 'Z_neg']
# job_ids = []
# for behavior_to_corr in behaviors:
#     for z in range(49):
#         save_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20211209_red_correlation/"
#         args = {'logfile': logfile,
#                 'save_directory': save_directory,
#                 'behavior_to_corr': behavior_to_corr,
#                 'z': z}
#         script = '20210322_final_9_correlation.py'
#         job_id = flow.sbatch(jobname='corr',
#                              script=os.path.join(scripts_path, script),
#                              modules=modules,
#                              args=args,
#                              logfile=logfile, time=2, mem=3, nice=nice, nodes=nodes) # 2 to 1
#         job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# #################
# ### Bootstrap ###
# #################

# printlog(f"\n{'   BOOTSTRAP   ':=^{width}}")

# #DONE:
# # job_params = ['correlation|Z_pos|Z_neg|True',
# #               'correlation|Y_pos|None|False',
# #               'correlation|Y_neg|None|False']

# #DONE:              
# # job_params = ['correlation|Z_pos|None|False',
# #               'correlation|Z_neg|None|False',
# #               'state|stop_times|moving_times|True']
# # job_params = ['correlation|Y_pos|Z_pos|True',
# #               'correlation|Y_pos|Z_neg|True']

# # job_params =  ['state|stop_times|forward_times|True',
# #                'state|stop_times|rotation_pos_times|True',
# #                'state|stop_times|rotation_neg_times|True',
# #                'state|rotation_pos_times|rotation_neg_times|True']
               
# # job_params = ['state|forward_times|rotation_neg_times|True',
# #               'state|forward_times|rotation_pos_times|True']
# # job_params = ['no_bootstrap|Y_pos|None|False']

# job_params = ['no_bootstrap|Y_pos|None|False',
#               'no_bootstrap|Z_pos|None|False',
#               'no_bootstrap|Z_neg|None|False']

# job_ids = []
# for job in job_params:
#     bootstrap_type = job.split('|')[0]
#     values_a = job.split('|')[1]
#     values_b = job.split('|')[2]
#     comparison = job.split('|')[3]
#     for z in range(49):
#         save_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20201206_bootstrap/"
#         args = {'logfile': logfile,
#                 'save_directory': save_directory,
#                 'bootstrap_type': bootstrap_type,
#                 'values_a': values_a,
#                 'values_b': values_b,
#                 'comparison': comparison,
#                 'z': z}
#         script = 'bootstrap_map.py'
#         job_id = flow.sbatch(jobname='bootstrp',
#                              script=os.path.join(scripts_path, script),
#                              modules=modules,
#                              args=args,
#                              logfile=logfile, time=2, mem=6, nice=nice, nodes=nodes) # 2 to 1
#         job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ################################
# ### NEURAL WEIGHTED BEHAVIOR ###
# ################################
# job_ids = []
# for z in [20]:#range(49):
#     args = {'logfile': logfile, 'z': z}
#     script = '20210318_neu_weighted_beh.py'
#     job_id = flow.sbatch(jobname='neuwebeh',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=24, mem=16, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ##########################
# ### CLUSTERING FILTERS ###
# ##########################
# job_ids = []
# for z in [20]:
#     args = {'logfile': logfile}
#     script = 'cluster_filters.py'
#     job_id = flow.sbatch(jobname='clstfilt',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=12, mem=22, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ##############
# ### SMOOTH ###
# ##############

# printlog(f"\n{'   SMOOTH   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'func_0')
#     args = {'logfile': logfile,
#             'directory': directory,
#             'file': 'brain_zscored_red.nii'} #<---------------------------------------
#     script = 'smooth.py'
#     job_id = flow.sbatch(jobname='smooth',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=4, mem=16, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ############
# ### MASK ###
# ############

# printlog(f"\n{'   MASK   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'func_0')
#     args = {'logfile': logfile,
#             'directory': directory,
#             'file': 'brain_zscored_red_high_pass.nii'} #<---------------------------------------
#     script = 'mask.py'
#     job_id = flow.sbatch(jobname='mask',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=1, mem=10, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ###########
# ### PCA ###
# ###########

# printlog(f"\n{'   PCA   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'func_0')
#     save_subfolder = '20201009_on_high_pass_masked' #         <---------------------------------------------------------------------------
#     #save_subfolder = None
#     args = {'logfile': logfile,
#             'directory': directory,
#             'file': 'brain_zscored_green_high_pass_masked.nii',
#             'save_subfolder': save_subfolder}
#     script = 'pca.py'
#     job_id = flow.sbatch(jobname='pca',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=4, mem=16, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ###########
# ### GLM ###
# ###########

# printlog(f"\n{'   GLM   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'func_0')
#     pca_subfolder = '20201009_on_high_pass_masked'#         <---------------------------------------------------------------------------
#     glm_date = '20201009'#         <---------------------------------------------------------------------------------------------------------------
#     args = {'logfile': logfile,
#             'directory': directory,
#             'pca_subfolder': pca_subfolder,
#             'glm_date': glm_date}
#     script = 'glm.py'
#     job_id = flow.sbatch(jobname='glm',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=1, mem=8, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ##################
# ### Clean Anat ###
# ##################

# printlog(f"\n{'   Clean Anat   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'anat_0', 'moco')
#     args = {'logfile': logfile, 'directory': directory}
#     script = 'clean_anat.py'
#     job_id = flow.sbatch(jobname='clnanat',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=1, mem=1, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ###############
# ### Sharpen ###
# ###############

# printlog(f"\n{'   Sharpen   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'anat_0', 'moco')
#     args = {'logfile': logfile, 'directory': directory}
#     script = 'sharpen_anat.py'
#     job_id = flow.sbatch(jobname='shrpanat',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=1, mem=1, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# #################
# ### func2anat ###
# #################

# res_anat = (0.65, 0.65, 1)
# res_func = (2.6, 2.6, 5)

# printlog(f"\n{'   func2anat   ':=^{width}}")

# job_ids = []
# for fly in flies:
#     fly_directory = os.path.join(dataset_path, fly)

#     moving_path = os.path.join(fly_directory, 'func_0', 'imaging', 'functional_channel_1_mean.nii')
#     moving_fly = 'func'
#     moving_resolution = res_func


#     fixed_path = os.path.join(fly_directory, 'anat_0', 'moco', 'stitched_brain_red_mean.nii')
#     fixed_fly = 'anat'
#     fixed_resolution = res_anat

#     save_directory = os.path.join(fly_directory, 'warp')
#     if not os.path.exists(save_directory):
#         os.mkdir(save_directory)

#     type_of_transform = 'Affine'
#     save_warp_params = True
#     flip_X = False
#     flip_Z = False
#     low_res = True

#     args = {'logfile': logfile,
#             'save_directory': save_directory,
#             'fixed_path': fixed_path,
#             'moving_path': moving_path,
#             'fixed_fly': fixed_fly,
#             'moving_fly': moving_fly,
#             'type_of_transform': type_of_transform,
#             'flip_X': flip_X,
#             'flip_Z': flip_Z,
#             'moving_resolution': moving_resolution,
#             'fixed_resolution': fixed_resolution,
#             'save_warp_params': save_warp_params,
#             'low_res': low_res}

#     script = 'align_anat.py'
#     job_id = flow.sbatch(jobname='align',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=8, mem=4, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# #################
# ### anat2mean ###
# #################

# res_anat = (0.65, 0.65, 1)

# printlog(f"\n{'   anat2mean   ':=^{width}}")

# job_ids = []
# for fly in flies:
#     fly_directory = os.path.join(dataset_path, fly)

#     moving_path = os.path.join(fly_directory, 'anat_0', 'moco', 'anat_red_clean_sharp.nii')
#     moving_fly = 'anat'
#     moving_resolution = res_anat


#     fixed_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates/luke.nii"
#     fixed_fly = 'meanbrain'
#     fixed_resolution = res_anat

#     save_directory = os.path.join(fly_directory, 'warp')
#     if not os.path.exists(save_directory):
#         os.mkdir(save_directory)

#     type_of_transform = 'SyN'
#     save_warp_params = True
#     flip_X = False
#     flip_Z = False
#     low_res = False

#     args = {'logfile': logfile,
#             'save_directory': save_directory,
#             'fixed_path': fixed_path,
#             'moving_path': moving_path,
#             'fixed_fly': fixed_fly,
#             'moving_fly': moving_fly,
#             'type_of_transform': type_of_transform,
#             'flip_X': flip_X,
#             'flip_Z': flip_Z,
#             'moving_resolution': moving_resolution,
#             'fixed_resolution': fixed_resolution,
#             'save_warp_params': save_warp_params,
#             'low_res': low_res}

#     script = 'align_anat.py'
#     job_id = flow.sbatch(jobname='align',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=8, mem=8, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ##################################
# ### Apply transforms: raw2mean ###
# ##################################
# res_anat = (0.65, 0.65, 1)
# res_func = (2.6, 2.6, 5, 1) #extra dim for time

# printlog(f"\n{'   Alignment   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     fly_directory = os.path.join(dataset_path, fly)
#     moving_path = os.path.join(fly_directory, 'func_0', 'brain_zscored_red_high_pass_masked.nii')#<---------------------------------------
#     moving_fly = 'raw'
#     moving_resolution = res_func

#     fixed_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates/luke.nii"
#     fixed_fly = 'meanbrain'
#     fixed_resolution = res_anat

#     warp_directory = os.path.join(fly_directory, 'warp')
#     save_directory = os.path.join(fly_directory, 'func_0')

#     args = {'logfile': logfile,
#             'warp_directory': warp_directory,
#             'save_directory': save_directory,
#             'fixed_path': fixed_path,
#             'moving_path': moving_path,
#             'fixed_fly': fixed_fly,
#             'moving_fly': moving_fly,
#             'moving_resolution': moving_resolution,
#             'fixed_resolution': fixed_resolution}

#     script = 'apply_transforms_to_raw_data.py'
#     job_id = flow.sbatch(jobname='aplytrns',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=2, mem=22, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ###################
# ### Correlation ###
# ###################

# printlog(f"\n{'   correlation   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'func_0')

#     behaviors = ['Y', 'Y_pos', 'Y_neg', 'Z_abs', 'Z_pos', 'Z_neg']
#     for behavior in behaviors:
#         args = {'logfile': logfile,
#                 'directory': directory,
#                 'behavior': behavior}
#         script = 'correlation_z_correction.py'
#         job_id = flow.sbatch(jobname='corr',
#                              script=os.path.join(scripts_path, script),
#                              modules=modules,
#                              args=args,
#                              logfile=logfile, time=1, mem=4, nice=nice, nodes=nodes) # 2 to 1
#         job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ########################
# ### Apply transforms ###
# ########################
# res_anat = (0.65, 0.65, 1)
# res_func = (2.6, 2.6, 5)

# printlog(f"\n{'   Alignment   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     fly_directory = os.path.join(dataset_path, fly)

#     behaviors = ['Y', 'Y_pos', 'Y_neg', 'Z_abs', 'Z_pos', 'Z_neg']
#     for behavior in behaviors:
#         moving_path = os.path.join(fly_directory, 'func_0', 'corr', '20201104_corr_{}.nii'.format(behavior))#<---------------------------------------
#         moving_fly = 'corr_{}'.format(behavior)
#         moving_resolution = res_func

#         fixed_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates/luke.nii"
#         fixed_fly = 'meanbrain'
#         fixed_resolution = res_anat

#         save_directory = os.path.join(fly_directory, 'warp')
#         if not os.path.exists(save_directory):
#             os.mkdir(save_directory)

#         args = {'logfile': logfile,
#                 'save_directory': save_directory,
#                 'fixed_path': fixed_path,
#                 'moving_path': moving_path,
#                 'fixed_fly': fixed_fly,
#                 'moving_fly': moving_fly,
#                 'moving_resolution': moving_resolution,
#                 'fixed_resolution': fixed_resolution}

#         script = 'apply_transforms.py'
#         job_id = flow.sbatch(jobname='aplytrns',
#                              script=os.path.join(scripts_path, script),
#                              modules=modules,
#                              args=args,
#                              logfile=logfile, time=12, mem=4, nice=nice, nodes=nodes) # 2 to 1
#         job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# printlog(f"\n{'   MASK   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'func_0')
#     args = {'logfile': logfile,
#             'directory': directory,
#             'file': 'brain_zscored_green_high_pass.nii'}
#     script = 'mask.py'
#     job_id = flow.sbatch(jobname='mask',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=1, mem=8, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# printlog(f"\n{'   PCA   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'func_0')
#     save_subfolder = '20201002_on_high_pass_masked'
#     #save_subfolder = None
#     args = {'logfile': logfile,
#             'directory': directory,
#             'file': 'brain_zscored_green_high_pass_masked.nii',
#             'save_subfolder': save_subfolder}
#     script = 'pca.py'
#     job_id = flow.sbatch(jobname='pca',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=4, mem=16, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

##########################
### Template alignment ################################################################################################
##########################

# res_JFRC = (0.62, 0.62, 0.62)
# res_JRC2018 = (0.38, 0.38, 0.38)
# res_IBNWB = (0.64, 0.64, 1.41)
# res_LUKE = (0.65, 0.65, 1)
# res_DIEGO = (0.75, 0.75, 1.0)
# res_KEVIN = (0.62,0.62,0.6)

# printlog(f"\n{'   Template Alignment   ':=^{width}}")
# moving_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates/20210507_luke_diego_corr2.nii"#luke.nii"#20210310_luke_depth_correction_2.nii"#nsybIVAf_c.nii"
# moving_fly = "lukediegocorr"
# moving_resolution = res_LUKE

# fixed_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates/JRC2018_FEMALE_38um_iso_16bit.nii"
# fixed_fly = 'jrc2018'
# fixed_resolution = res_JRC2018

# save_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/anat_templates/"
# if not os.path.exists(save_directory):
#     os.mkdir(save_directory)

# type_of_transform = 'SyN' #'Affine' #SyN
# flip_X = False
# flip_Z = False
# save_warp_params = False
# low_res = False
# very_low_res = False

# grad_step = 0.2
# flow_sigma = 3
# total_sigma = 0
# syn_sampling = 32

# job_ids = []
# #for syn_sampling in [.32,3.2,16,32,64,320]:
# #for total_sigma in [.01,.1,0,10,100]:
# #for flow_sigma in [30,50,70,90]:
# #for grad_step in [0.02,.2,2,.1,.4,.0002,20]:
# #fixed_fly = F"jrc2018_ss{syn_sampling}"

# args = {'logfile': logfile,
#         'save_directory': save_directory,
#         'fixed_path': fixed_path,
#         'moving_path': moving_path,
#         'fixed_fly': fixed_fly,
#         'moving_fly': moving_fly,
#         'type_of_transform': type_of_transform,
#         'flip_X': flip_X,
#         'flip_Z': flip_Z,
#         'moving_resolution': moving_resolution,
#         'fixed_resolution': fixed_resolution,
#         'save_warp_params': save_warp_params,
#         'low_res': low_res,
#         'very_low_res': very_low_res,
#         'grad_step': grad_step,
#         'flow_sigma': flow_sigma,
#         'total_sigma': total_sigma,
#         'syn_sampling': syn_sampling}

# script = 'align_anat.py'
# job_id = flow.sbatch(jobname='align',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=4, mem=16, nice=nice, nodes=nodes) # 2 to 1
# job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

###################################################################################################################

###################################################################################################################
# printlog(f"\n{'   ZSCORE   ':=^{width}}")
# job_ids = []
# for fly in flies:
#     directory = os.path.join(dataset_path, fly, 'func_0')
#     args = {'logfile': logfile, 'directory': directory, 'smooth': True, 'colors': ['green']}
#     script = 'zscore.py'
#     job_id = flow.sbatch(jobname='zscore',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=8, mem=18, nice=nice, nodes=nodes) # 2 to 1
#     job_ids.append(job_id)

# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)



###################################################################################################################

# save_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain"
# input_directory = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20200803_meanbrain/syn_0"
# save_name = "syn_0_mean"

# printlog(f"\n{'   LOOP   ':=^{width}}")
# args = {'logfile': logfile,
#         'save_directory': save_directory,
#         'input_directory': input_directory,
#         'save_name': save_name}
# script = 'avg_brains.py'
# job_id = flow.sbatch(jobname='avgbrn',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=1, mem=4, nice=nice, nodes=nodes) # 2 to 1
# flow.wait_for_job(job_id, logfile, com_path)

############
### Done ###
############

time.sleep(30) # to allow any final printing
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog("="*width)
printlog(F"{day_now+' | '+time_now:^{width}}")
