import time
import sys
import os
import re
import json
import datetime
import pyfiglet
import textwrap
import dataflow as flow
import bigbadbrain as bbb

modules = 'gcc/6.3.0 python/3.6.1 py-numpy/1.14.3_py36 py-pandas/0.23.0_py36 viz py-scikit-learn/0.19.1_py36'

#########################
### Setup preferences ###
#########################

width = 120 # width of print log
fly_dirs = ['fly1'] # set to None, or a list of fly dirs in the import dir

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

title = pyfiglet.figlet_format("Dataflow", font="cyberlarge" ) #28 #shimrod
title_shifted = ('\n').join([' '*28+line for line in title.split('\n')][:-2])
printlog(title_shifted)
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog(F"{day_now+' | '+time_now:^{width}}")
printlog("")
printlog("="*width)

# ######################
# ### Check for flag ###
# ######################
# args = {'logfile': logfile, 'imports_path': imports_path}
# script = 'check_for_flag.py'
# job_id = flow.sbatch(jobname='flagchk',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=1, mem=1, nice=True)
# flagged_dir = flow.wait_for_job(job_id, logfile, com_path)

# ###################
# ### Build flies ###
# ###################

# args = {'logfile': logfile, 'flagged_dir': flagged_dir.strip('\n'), 'dataset_path': dataset_path, 'fly_dirs': fly_dirs}
# script = 'fly_builder.py'
# job_id = flow.sbatch(jobname='bldfly',
#                      script=os.path.join(scripts_path, script),
#                      modules=modules,
#                      args=args,
#                      logfile=logfile, time=1, mem=1, nice=True)
# func_and_anats = flow.wait_for_job(job_id, logfile, com_path)
# func_and_anats = func_and_anats.split('\n')[:-1]
# funcs = [x.split(':')[1] for x in func_and_anats if 'func:' in x] # will be full paths to fly/expt
# anats = [x.split(':')[1] for x in func_and_anats if 'anat:' in x]
# bbb.sort_nicely(funcs)
# bbb.sort_nicely(anats)
# funcanats = funcs + anats
# dirtypes = ['func']*len(funcs) + ['anat']*len(anats)

# ### TEMP - REMOVE!!!!!!!! <==============================================    REMOVE
# #funcanats = funcs
# #dirtypes = ['func']*len(funcs)

# funcanats = anats
# dirtypes = ['anat']*len(anats)

# ##################
# ### Fictrac QC ###
# ##################

# job_ids = []
# for func in funcs:
#     directory = os.path.join(func, 'fictrac')
#     if os.path.exists(directory):
#         args = {'logfile': logfile, 'directory': directory}
#         script = 'fictrac_qc.py'
#         job_id = flow.sbatch(jobname='fictracqc',
#                              script=os.path.join(scripts_path, script),
#                              modules=modules,
#                              args=args,
#                              logfile=logfile, time=1, mem=1, nice=False)
#         job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ####################
# ### Bleaching QC ###
# ####################

# job_ids = []
# for funcanat, dirtype in zip(funcanats, dirtypes):
#     directory = os.path.join(funcanat, 'imaging')
#     args = {'logfile': logfile, 'directory': directory, 'dirtype': dirtype}
#     script = 'bleaching_qc.py'
#     job_id = flow.sbatch(jobname='bleachqc',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=1, mem=1, nice=False)
#     job_ids.append(job_id)
# for job_id in job_ids:
#     flow.wait_for_job(job_id, logfile, com_path)

# ##########################
# ### Create mean brains ###
# ##########################

# job_ids = []
# for funcanat, dirtype in zip(funcanats, dirtypes):
#     directory = os.path.join(funcanat, 'imaging')
#     args = {'logfile': logfile, 'directory': directory, 'dirtype': dirtype}
#     script = 'make_mean_brain.py'
#     job_id = flow.sbatch(jobname='meanbrn',
#                          script=os.path.join(scripts_path, script),
#                          modules=modules,
#                          args=args,
#                          logfile=logfile, time=1, mem=1, nice=False)
#     job_ids.append(job_id)

# timepointss = []
# for job_id in job_ids:
#     timepoints = flow.wait_for_job(job_id, logfile, com_path)
#     timepointss.append(int(timepoints.split('\n')[0]))

##################
### Start MOCO ###
##################

# This will immediately launch all partial mocos and their corresponding dependent moco stitchers
stitcher_job_ids = []
progress_tracker = {}

timepointss = [100]
funcanats = [os.path.join(dataset_path, 'fly_170', 'anat_0')]
dirtype = ['anat']

for funcanat, dirtype, timepoints in zip(funcanats, dirtypes, timepointss):

    fly_print = funcanat.split('/')[-2]
    expt_print = funcanat.split('/')[-1]

    moco_dir = os.path.join(funcanat, 'moco')
    if not os.path.exists(moco_dir):
        os.makedirs(moco_dir)

    if dirtype == 'func':
        step = 10 ### <================ compare speed with different step/mem combos
        mem = 2
        time_moco = 1
    elif dirtype == 'anat':
        step = 15
        mem = 6
        time_moco = 6

    starts = list(range(0,timepoints,step))
    stops = starts[1:] + [timepoints]

    #######################
    ### Launch partials ###
    #######################
    job_ids = []
    for start, stop in zip (starts, stops):
        args = {'logfile': logfile, 'directory': funcanat, 'dirtype': dirtype, 'start': start, 'stop': stop}
        script = 'moco_partial.py'
        job_id = flow.sbatch(jobname='moco',
                             script=os.path.join(scripts_path, script),
                             modules=modules,
                             args=args,
                             logfile=logfile, time=time_moco, mem=mem, nice=True, silence_print=True)
        job_ids.append(job_id)

    #to_print = F"| moco_partials | SUBMITTED | {fly_print} | {expt_print} | {len(job_ids)} jobs, {step} vols each |"
    #printlog(textwrap.TextWrapper(width=width).fill(text=to_print))
    printlog(F"| moco_partials | SUBMITTED | {fly_print} | {expt_print} | {len(job_ids)} jobs, {step} vols each |")
    job_ids_colons = ':'.join(job_ids)
    progress_tracker[funcanat] = {'job_ids': job_ids, 'total_vol': timepoints}
    #printlog(textwrap.TextWrapper(width=120).fill(text=str(job_ids_colons)))

    #################################
    ### Create dependent stitcher ###
    #################################

    args = {'logfile': logfile, 'directory': moco_dir}
    script = 'moco_stitcher.py'
    job_id = flow.sbatch(jobname='stitch',
                         script=os.path.join(scripts_path, script),
                         modules=modules,
                         args=args,
                         logfile=logfile, time=2, mem=12, dep=job_ids_colons, nice=True)
    stitcher_job_ids.append(job_id)

flow.moco_progress(progress_tracker, logfile, com_path)

for job_id in stitcher_job_ids:
    flow.wait_for_job(job_id, logfile, com_path)

###############
### Z-Score ###
###############

job_ids = []
for funcanat in funcanats:
    args = {'logfile': logfile, 'directory': funcanat}
    script = 'zscore.py'
    job_id = flow.sbatch(jobname='zscore',
                         script=os.path.join(scripts_path, script),
                         modules=modules,
                         args=args,
                         logfile=logfile, time=2, mem=14, nice=True)
    job_ids.append(job_id)

for job_id in job_ids:
    flow.wait_for_job(job_id, logfile, com_path)

############
### Done ###
############

day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog("="*width)
printlog(F"{day_now+' | '+time_now:^{width}}")

'''
- check for flag
    - build fly
        - moco trigger
            - moco splitter
                - moco stitcher
                    - zscore
                        - more analysis (PCA, GLM, etc)
                        - bleaching_QC
        - fictrac_QC

check for flag (in:None, out:PATH)

How to return values? writing to a file is probably simply the best? (write to a file with it's own job ID!)

'''