import time
import sys
import os
import json
import dataflow as flow

#####################
### Setup logging ###
#####################

logfile = './logs/' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')
sys.stderr = flow.Logger_stderr_sherlock(logfile)

###################
### Setup Paths ###
###################

imports_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports/build_queue"
scripts_path = "/home/users/brezovec/projects/dataflow/sherlock_scripts"
com_path = "/home/users/brezovec/projects/dataflow/sherlock_scripts/com"
dataset_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset"

######################
### Check for flag ###
######################

args = {'logfile': logfile, 'imports_path': imports_path}
script = 'check_for_flag.py'
modules = 'python/3.6.1'
job_id = flow.sbatch(jobname='flagchk',
                     script=os.path.join(scripts_path, script),
                     modules=modules,
                     args=args,
                     logfile=logfile, time=1, mem=1, dep='')
flagged_dir = flow.wait_for_job(job_id, logfile, com_path)

###################
### Build flies ###
###################

args = {'logfile': logfile, 'flagged_dir': flagged_dir.strip('\n'), 'dataset_path': dataset_path}
script = 'fly_builder.py'
modules = 'gcc/6.3.0 python/3.6.1 py-numpy/1.14.3_py36 py-pandas/0.23.0_py36 viz py-scikit-learn/0.19.1_py36'
job_id = flow.sbatch(jobname='bldfly',
                     script=os.path.join(scripts_path, script),
                     modules=modules,
                     args=args,
                     logfile=logfile, time=2, mem=1, dep='')
flies = flow.wait_for_job(job_id, logfile, com_path)
printlog(f'flies not split: {flies}')
printlog(f'flies split: {flies.split('\n')}')
# \n split?

###################################
### START MOTCORR ON FUNCTIONAL ###
###################################
#2798265


#os.system("sbatch motcorr_trigger.sh {}".format(expt_folder))

##################################
### PRODUCE FICTRAC QC FIGURES ###
##################################
#os.system("sbatch fictrac_qc.sh {}".format(expt_folder))


############
### etc. ###
############

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