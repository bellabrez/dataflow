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

##################
### Start MOCO ###
##################
step = 1
mem = 4
time_moco = 3
progress_tracker = {}
job_ids = []
start = 10
stop = 11
timepoints=int(stop-start)
funcanat = os.path.join(dataset_path, 'fly_170', 'anat_0')
dirtype = 'anat'

fly_print = funcanat.split('/')[-2]
expt_print = funcanat.split('/')[-1]
args = {'logfile': logfile, 'directory': funcanat, 'dirtype': dirtype, 'start': start, 'stop': stop}
script = 'moco_partial.py'
job_id = flow.sbatch(jobname='moco',
                     script=os.path.join(scripts_path, script),
                     modules=modules,
                     args=args,
                     logfile=logfile, time=time_moco, mem=mem, nice=True, silence_print=True)
job_ids.append(job_id)
printlog(F"| moco_partials | SUBMITTED | {fly_print} | {expt_print} | {len(job_ids)} jobs, {step} vols each |")
job_ids_colons = ':'.join(job_ids)
progress_tracker[funcanat] = {'job_ids': job_ids, 'total_vol': timepoints}
flow.moco_progress(progress_tracker, logfile, com_path)
for job_id in job_ids:
    flow.wait_for_job(job_id, logfile, com_path)

############
### Done ###
############

day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog("="*width)
printlog(F"{day_now+' | '+time_now:^{width}}")