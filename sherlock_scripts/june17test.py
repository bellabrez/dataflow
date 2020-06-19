import subprocess
import time
import sys
import dataflow as flow

class Logger_stderr(object):
    def __init__(self, logfile):
        self.logfile = logfile

    def write(self, message):
        with open(self.logfile, 'a+') as f:
            #fcntl.flock(f, fcntl.LOCK_EX)
            f.write(message)
            #fcntl.flock(f, fcntl.LOCK_UN)

    def flush(self):
        pass

def sbatch(job_name, command, logfile, time=1, mem=1, dep=''):
    if dep != '':
        dep = '--dependency=afterok:{} --kill-on-invalid-dep=yes '.format(dep)
 
    #sbatch_command = "sbatch -J {} -t {}:00:00 --partition=trc --open-mode=append --cpus-per-task={} --wrap='{}' {}".format(job_name, time, mem, command, dep)
    #sbatch_command = "sbatch -J {} -o {}.out -e {}.err -t {}:00:00 --partition=trc --open-mode=append --cpus-per-task={} --wrap='{}' {}".format(job_name, 'mainlog', 'mainlog', time, mem, command, dep)
    sbatch_command = "sbatch -J {} -o {} -e {} -t {}:00:00 --partition=trc --open-mode=append --cpus-per-task={} --wrap='{}' {}".format(job_name, logfile, logfile, time, mem, command, dep)
    sbatch_response = subprocess.getoutput(sbatch_command)
    printlog(sbatch_response)
    job_id = sbatch_response.split(' ')[-1].strip()
    return job_id

logfile = './logs/' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')
sys.stderr = Logger_stderr(logfile)

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} {}'.format(logfile, 'a')
job_id = sbatch('luke_test', command, logfile)
printlog('job_id = {}'.format(job_id))

asdfdf

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} {}'.format(logfile, 'b')
job_id = sbatch('luke_test', command, logfile)
printlog('job_id = {}'.format(job_id))

for i in range(20):
    test = subprocess.getoutput('sacct -X -j {} --format=State'.format(job_id))
    printlog('main says {}'.format(test))
    time.sleep(5)
