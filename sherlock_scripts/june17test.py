import subprocess
import time
import sys

def sbatch(job_name, command, time=1, mem=1, dep=''):
    if dep != '':
        dep = '--dependency=afterok:{} --kill-on-invalid-dep=yes '.format(dep)
 
    sbatch_command = "sbatch -J {} -o {}.out -e {}.err -t {}:00:00 --partition=trc --open-mode=append --cpus-per-task={} --wrap='{}' {}".format(job_name, 'thisisout', job_name, time, mem, command, dep)
    sbatch_response = subprocess.getoutput(sbatch_command)
    print(sbatch_response)
    job_id = sbatch_response.split(' ')[-1].strip()
    return job_id

#sys.stdout = open('hellotoyou.txt', 'w')

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} > tada.txt'.format('a')
job_id = sbatch('luke_test', command)
print('job_id = {}'.format(job_id))

#time.sleep(90)

command = 'ml python/3.6.1; python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test_minion.py {} > tada.txt'.format('b')
job_id = sbatch('luke_test', command)
print('job_id = {}'.format(job_id))

#time.sleep(90)

# for i in range(20):
#     test = subprocess.getoutput('sacct -X -j {} --format=State'.format(job_id))
#     print('main says {}'.format(test))
#     sys.stdout.flush()
#     time.sleep(5)

