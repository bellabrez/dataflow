import time
import sys
import os
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

######################
### Check for flag ###
######################

title = pyfiglet.figlet_format("Dataflow", font="cyberlarge" )
title_shifted = ('\n').join([' '*28+line for line in title.split('\n')][:-2])
printlog(title_shifted)
#printlog(f"{'--*-*- Dataflow -*-*--':^{width}}")
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog(F"{day_now+' | '+time_now:^{width}}")
#printlog("\n")
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

args = {'logfile': logfile, 'flagged_dir': flagged_dir.strip('\n'), 'dataset_path': dataset_path, 'fly_dirs': fly_dirs}
script = 'fly_builder.py'
job_id = flow.sbatch(jobname='bldfly',
                     script=os.path.join(scripts_path, script),
                     modules=modules,
                     args=args,
                     logfile=logfile, time=1, mem=1, nice=True)
func_and_anats = flow.wait_for_job(job_id, logfile, com_path)
func_and_anats = func_and_anats.split('\n')[:-1]
funcs = bbb.sort_nicely([x.split(':')[1] for x in func_and_anats if 'func:' in x]) # will be full paths to fly/expt
anats = bbb.sort_nicely([x.split(':')[1] for x in func_and_anats if 'anat:' in x])
funcanats = funcs + anats
dirtypes = ['func']*len(funcs) + ['anat']*len(anats)

### TEMP - REMOVE!!!!!!!!
#funcanats = funcs[0]
#dirtypes = ['func']

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
                         logfile=logfile, time=1, mem=1, nice=False)
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
progress_tracker = {}
for funcanat, dirtype, timepoints in zip(funcanats, dirtypes, timepointss):

    fly_print = funcanat.split('/')[-2]
    expt_print = funcanat.split('/')[-1]

    moco_dir = os.path.join(funcanat, 'moco')
    if not os.path.exists(moco_dir):
        os.makedirs(moco_dir)

    if dirtype == 'func':
        step = 10
    elif dirtype == 'anat':
        step = 5

    starts = list(range(0,timepoints,step))
    stops = starts[1:] + [timepoints]

    #######################
    ### Launch partials ###
    #######################

    '''
    Com and print makes this super easy! 
    Each moco_partial job is responsible for 10 vol
    main knowns what fly and expt goes with each jobid
    each funcanat wants to be checking the slurm-jobid files in com, where it will find an int of progress
    psuedocode:
    
    '''

    job_ids = []
    for start, stop in zip (starts, stops):
        args = {'logfile': logfile, 'directory': funcanat, 'dirtype': dirtype, 'start': start, 'stop': stop}
        script = 'moco_partial.py'
        job_id = flow.sbatch(jobname='moco',
                             script=os.path.join(scripts_path, script),
                             modules=modules,
                             args=args,
                             logfile=logfile, time=1, mem=1, nice=True, silence_print=True)
        job_ids.append(job_id)

    to_print = F"| mocos | {fly_print} | {expt_print} | {len(job_ids)} jobs, {step} vols each: {job_ids}"
    printlog(textwrap.TextWrapper(width=width).fill(text=to_print))
    job_ids_colons = ':'.join(job_ids)
    progress_tracker[funcanat] = job_ids

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

#flow.moco_progress(progress_tracker, logfile, com_path)

for job_id in stitcher_job_ids:
    flow.wait_for_job(job_id, logfile, com_path)

# def moco_progress(progress_tracker, logfile, com_path):
#     ##############################################################################
#     ### Printing a progress bar every min until all moco_partial jobs complete ###
#     ##############################################################################
#     printlog = getattr(Printlog(logfile=logfile), 'print_to_log')
#     print_header = True
#     while True:
#         progress = {}
#         stati = []
#         ###############################
#         ### Get progress and status ###
#         ###############################
#         ### For each expt_dir, for each moco_partial job_id, get progress from slurm.out files, and status ###
#         for funcanat in progress_tracker:
#             complete_vol = 0
#             for job_id in progress_tracker[funcanat]:
#                 # Read com file
#                 com_file = os.path.join(com_path, job_id + '.out')
#                 try:
#                     with open(com_file, 'r') as f:
#                         output = f.read()
#                         ### TODO parse output <================================================
#                         total_vol = TODO
#                         complete_vol_partial = TODO
#                 except:
#                     output = None

#                 total_vol = total_vol # should always be the same anyway
#                 complete_vol += complete_vol_partial
#             progress[funcanat] = {'total_vol': total_vol, 'complete_vol': complete_vol} # Track progress
#             stati.append(get_job_status(job_id, logfile)) # Track status

#         ##########################
#         ### Print progress bar ###
#         ##########################

#         # what would be a good thing to print within moco_partials?
#         # print numbers with a separation, then parse
#         # will have this: progress[funcanat].append({'job_id': output})
#         # want a double bar for each funcanat showing job% and vol%.
#         # could easily have 4 flies, or 8 funcanats (anat and func), or 16 bars (job% and vol%)
#         # 120 char width

#         print_progress_table(progress, logfile)
#         print_header = False

#         ###############################################
#         ### Return if all jobs are done, else sleep ###
#         ###############################################
#         finished = ['COMPLETED', 'CANCELLED', 'TIMEOUT', 'FAILED', 'OUT_OF_MEMORY']
#         if all([status in finished for status in stati]):
#             return
#         else:
#             sleep(1)

# def progress_bar(iteration, total, length, fill = '█'):
#     filledLength = int(length * iteration // total)
#     bar = fill * filledLength + '-' * (length - filledLength)
#     fraction = F"{str(iteration):^4}" + '/' + F"{str(total):^4}"
#     bar_string = f"{bar}"
#     return bar_string

# def print_progress_table(progress, logfile, print_header):
#     printlog = getattr(Printlog(logfile=logfile), 'print_to_log')

#     num_columns=8

#     complete_vol = 3000
#     total_vol = 3142
#     column_width=9

#     if print_header:
#         printlog((' '*9) + '+' + '+'.join([F"{'':-^{column_width}}"]*num_columns) + '+')
#         printlog((' '*9) + '|' + '|'.join([F"{'fly_124':^{column_width}}"]*num_columns) + '|')
#         printlog((' '*9) + '|' + '|'.join([F"{'func_0':^{column_width}}"]*num_columns) + '|'
#         printlog((' '*9) + '|' + '|'.join([F"{str(total_vol)+' vols':^{column_width}}"]*num_columns) + '|')
#         printlog('|ELAPSED ' + '+' + '+'.join([F"{'':-^{column_width}}"]*num_columns) + '+' + 'REMAININ|')

#     for complete_vol in range(0,total_vol,100):
#         bar_string = progress_bar(complete_vol, total_vol, column_width)
#         fly_line = '|' + '|'.join([F"{bar_string:^{column_width}}"]*num_columns) + '|'
#         fly_line = '|00:00:00' + fly_line + '00:00:00|'
#         printlog(fly_line)


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