import time
import sys
import dataflow as flow

#####################
### Setup logging ###
#####################

logfile = './logs/' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')
sys.stderr = flow.Logger_stderr_sherlock(logfile)

############
### etc. ###
############

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} {}'.format(logfile, 'a')
job_id = flow.sbatch('luke_test', command, logfile)
printlog('Submitted... {}'.format(job_id))

flow.wait_for_job(job_id, logfile)

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} {}'.format(logfile, 'b')
job_id = flow.sbatch('luke_test', command, logfile)
printlog('Submitted... {}'.format(job_id))

flow.wait_for_job(job_id, logfile)

printlog('shazam')