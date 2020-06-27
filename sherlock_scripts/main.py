import time
import sys
import os
import json
import dataflow as flow
import datetime

modules = 'gcc/6.3.0 python/3.6.1 py-numpy/1.14.3_py36 py-pandas/0.23.0_py36 viz py-scikit-learn/0.19.1_py36'
width = 77 # width of print log

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

######################
### Check for flag ###
######################

printlog(f"{'--*-*- Dataflow -*-*--':^{width}}")
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog(F"{day_now+' | '+time_now:^77}")
printlog("="*width)
args = {'logfile': logfile, 'imports_path': imports_path}
script = 'check_for_flag.py'
job_id = flow.sbatch(jobname='flagchk',
                     script=os.path.join(scripts_path, script),
                     modules=modules,
                     args=args,
                     logfile=logfile, time=1, mem=1, nice=True)
flagged_dir = flow.wait_for_job(job_id, logfile, com_path)

###################
### Build flies ###
###################

args = {'logfile': logfile, 'flagged_dir': flagged_dir.strip('\n'), 'dataset_path': dataset_path}
script = 'fly_builder.py'
job_id = flow.sbatch(jobname='bldfly',
                     script=os.path.join(scripts_path, script),
                     modules=modules,
                     args=args,
                     logfile=logfile, time=1, mem=1, nice=True)
func_and_anats = flow.wait_for_job(job_id, logfile, com_path)
func_and_anats = func_and_anats.split('\n')[:-1]
funcs = [x.split(':')[1] for x in func_and_anats if 'func:' in x]
anats = [x.split(':')[1] for x in func_and_anats if 'anat:' in x]
funcanats = funcs + anats
dirtypes = ['func']*len(funcs) + ['anat']*len(anats)

##########################
### Create mean brains ###
##########################

job_ids = []
for funcanat, dirtype in zip(funcanats, dirtypes):
    directory = os.path.join(funcanat, 'imaging')
    args = {'logfile': logfile, 'directory': directory, 'dirtype': dirtype}
    script = 'make_mean_brain.py'
    job_id = flow.sbatch(jobname='meanbrn',
                         script=os.path.join(scripts_path, script),
                         modules=modules,
                         args=args,
                         logfile=logfile, time=1, mem=6, nice=True)
    job_ids.append(job_id)

timepointss = []
for job_id in job_ids:
    timepoints = flow.wait_for_job(job_id, logfile, com_path)
    timepointss.append(int(timepoints.split('\n')[0]))

##################
### Start MOCO ###
##################

# This will immediately launch all partial mocos and their corresponding dependent moco stitchers
stitcher_job_ids = []
for funcanat, dirtype, timepoints in zip(funcanats, dirtypes, timepointss):

    moco_dir = os.path.join(funcanat, 'moco')
    if not os.path.exists(moco_dir):
        os.makedirs(moco_dir)

    if dirtype == 'func':
        step = 100
    elif dirtype == 'anat':
        step = 10

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
                             logfile=logfile, time=1, mem=1, nice=True)
        job_ids.append(job_id)
    job_ids_colons = ':'.join(job_ids)

    #################################
    ### Create dependent stitcher ###
    #################################

    args = {'logfile': logfile, 'directory': moco_dir}
    script = 'moco_stitcher.py'
    job_id = flow.sbatch(jobname='stitch',
                         script=os.path.join(scripts_path, script),
                         modules=modules,
                         args=args,
                         logfile=logfile, time=2, mem=4, dep=job_ids_colons, nice=True)
    stitcher_job_ids.append(job_id)

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
                         logfile=logfile, time=2, mem=6, nice=True)
    job_ids.append(job_id)

for job_id in job_ids:
    flow.wait_for_job(job_id, logfile, com_path)

############
### Done ###
############



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

#######
--- 1) make a new script whos job is to simply make the meanbrains...
for funcanat in funcanat:
    (funcanat) -> makemeanbrain -> (shape) : [jobids]
for jobid: wait_for_job
now, all these jobs are done
#######
--- 2)
for funcanat in funcanat:
    for start/stop (calc via shape):
        moco_partial
    moco_stitcher with dependency on all moco_partials
wait for moco_stitchers


so, for funcanat in funcanat:
    (funcanat) -> moco_splitter -> ([vol starts and ends])
for jobid: wait_for_job


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