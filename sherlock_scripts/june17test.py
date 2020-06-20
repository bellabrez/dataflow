import subprocess
import time
import sys
import dataflow as flow

def sbatch(job_name, command, logfile, time=1, mem=1, dep=''):
    if dep != '':
        dep = '--dependency=afterok:{} --kill-on-invalid-dep=yes '.format(dep)
 
    sbatch_command = "sbatch -J {} -o {} -e {} -t {}:00:00 --partition=trc --open-mode=append --cpus-per-task={} --wrap='{}' {}".format(job_name, logfile, logfile, time, mem, command, dep)
    sbatch_response = subprocess.getoutput(sbatch_command)
    printlog(sbatch_response)
    job_id = sbatch_response.split(' ')[-1].strip()
    return job_id

def get_job_status(job_id, should_print=False):
    temp = subprocess.getoutput('sacct -n -P -j {} --noconvert --format=State,Elapsed,MaxRSS,NCPUS'.format(job_id))
    status = temp.split('\n')[0].split('|')[0]
    duration = temp.split('\n')[0].split('|')[1]
    num_cores = temp.split('\n')[0].split('|')[3]
    memory_used = temp.split('\n')[1].split('|')[2] # in bytes
    core_memory = 7.77 * 1024 * 1024 * 1024 #GB to MB to KB to bytes
    if should_print:

        if memory_used > 1024 ** 3:
            memory_to_print = str(memory_used/1024 ** 3) + 'GB'
        elif memory_used > 1024 ** 2:
            memory_to_print = str(memory_used/1024 ** 2) + 'MB'
        elif memory_used > 1024 ** 1:
            memory_to_print = str(memory_used/1024 ** 1) + 'KB'
        else:
            memory_to_print = str(memory_used) + 'B'

        percent_mem = memory_used/(core_memory*num_cores)
        printlog('Job {} Status: {}\nDuration: {}\nNum Cores: {}\nMemory Used: {} ({:0.2f}%)'.format(job_id, status, duration, num_cores, memory_to_print, percent_mem))

    return status

def wait_for_job(job_id):
    printlog('Waiting for job {}'.format(job_id))
    while True:
        status = get_job_status(job_id)
        if status in ['COMPLETED', 'CANCELLED', 'TIMEOUT', 'FAILED', 'OUT_OF_MEMORY']:
            status = get_job_status(job_id, should_print=True)
            break
        else:
            time.sleep(5)

logfile = './logs/' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')
sys.stderr = flow.Logger_stderr_sherlock(logfile)

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} {}'.format(logfile, 'a')
job_id = sbatch('luke_test', command, logfile)

wait_for_job(job_id)

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} {}'.format(logfile, 'b')
job_id = sbatch('luke_test', command, logfile)

wait_for_job(job_id)

printlog('shazam')