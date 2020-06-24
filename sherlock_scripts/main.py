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
func_and_anats = flow.wait_for_job(job_id, logfile, com_path)
func_and_anats = func_and_anats.split('\n')[:-1]
funcs = [x.split(':')[1] for x in func_and_anats if 'func:' in func_and_anats]
anats = [x.split(':')[1] for x in func_and_anats if 'anat:' in func_and_anats]
printlog(f"func_and_anats: {func_and_anats}")
printlog(f"funcs: {funcs}")
printlog(f"anats: {anats}")

###################################
### START MOTCORR ON FUNCTIONAL ###
###################################
'''
option:
I will now have a list of flies
each fly could have multiple func...
before, this was handled by each func folder triggering motcorr trigger,
after flybuilder copied the func folder

I think this main loop should expose each func folder, that way I can run
any analysis on only a single func folder! - way more flexibility

so actually I would like fly builder to return a list of fly/funcs, not just flies...
then it is trivial to loop over

now, how to restructure the motcorr splitter/partial/stitcher?
would like all calls to sbatch to come from this script - is that possible? I think so

first, make a new script whos job is to simply make the meanbrains...

(funcs and anats) -> makemeanbrain -> (NA) # wait_for_job


path -> splitter
splitter will create the meanbrain

only needs to

'''



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