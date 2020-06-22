import time
import sys
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

args = json.dumps({'logfile': logfile, 'imports_path': imports_path})
printlog('dumps: {}'.format(args))
command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/check_for_flag.py {}'.format(args)
job_id = flow.sbatch('flagchk', command, logfile, time=1, mem=1, dep='')
flow.wait_for_job(job_id, logfile)






# command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} {}'.format(logfile, 'a')
# job_id = flow.sbatch('luke_test', command, logfile)
# flow.wait_for_job(job_id, logfile)

# command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} {}'.format(logfile, 'b')
# job_id = flow.sbatch('luke_test', command, logfile)
# flow.wait_for_job(job_id, logfile)

# printlog('shazam')