import subprocess
import time

def sbatch(job_name, command, time=1, mem=1, dep=''):
    if dep != '':
        dep = '--dependency=afterok:{} --kill-on-invalid-dep=yes '.format(dep)
 
    sbatch_command = "sbatch -J {} -o {}.out -e {}.err -t {}:00:00 --partition=trc --cpus-per-task={} --wrap='{}' {}".format(job_name, job_name, job_name, time, mem, command, dep)
    sbatch_response = subprocess.getoutput(sbatch_command)
    print(sbatch_response) 
    job_id = sbatch_response.split(' ')[-1].strip()
    return job_id

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py'
job_id = sbatch('luke_test', command)

for i in range(20):
    test = subprocess.check_output('sacct -X -j {}'.format(job_id),shell=True)
    print('main says {}'.format(test))
    time.sleep(5)