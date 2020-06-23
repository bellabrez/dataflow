import sys
import smtplib
import re
import os
import h5py
import math
import json
from email.mime.text import MIMEText
from time import time
from time import strftime
from time import sleep
from functools import wraps
import numpy as np
import nibabel as nib
from scipy.ndimage import imread
from xml.etree import ElementTree as ET
import subprocess

# only imports on linux, which is fine since only needed for sherlock
try:
    import fcntl
except ImportError:
    pass

def get_json_data(file_path):
    with open(file_path) as f:  
        data = json.load(f)
    return data

def send_email(subject='', message='', recipient="brezovec@stanford.edu"):
    """ Sends emails!

    Parameters
    ----------
    subject: email subject heading (str)
    message: body of text (str)

    Returns
    -------
    Nothing. """
    print('Sending email to {}'.format(recipient))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("python.notific@gmail.com", "9!tTT77x!ma8cGy")

    msg = MIMEText(message)
    msg['Subject'] = subject

    server.sendmail(recipient, recipient, msg.as_string())
    server.quit()

def timing(f):
    """ Wrapper function to time how long functions take (and print function name). """

    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        print('\nFUNCTION CALL: {}'.format(f.__name__))
        sys.stdout.flush()
        result = f(*args, **kwargs)
        end = time()
        duration = end-start

        # Make units nice (originally in seconds)
        if duration < 1:
            duration = duration * 1000
            suffix = 'ms'
        elif duration < 60:
            duration = duration
            suffix = 'sec'
        elif duration < 3600:
            duration = duration / 60
            suffix = 'min'
        else:
            duration = duration / 3600
            suffix = 'hr'

        print('FUNCTION {} done. DURATION: {:.2f} {}'.format(f.__name__,duration,suffix))
        sys.stdout.flush()
        return result
    return wrapper

class Logger_stdout(object):
    def __init__(self):
        self.terminal = sys.stdout
        log_folder = 'C:/Users/User/Desktop/dataflow_logs'
        log_file = 'dataflow_log_' + strftime("%Y%m%d-%H%M%S") + '.txt'
        self.full_log_file = os.path.join(log_folder, log_file)
        self.log = open(self.full_log_file, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass 

class Logger_stderr(object):
    def __init__(self):
        self.terminal = sys.stderr
        log_folder = 'C:/Users/User/Desktop/dataflow_error'
        log_file = 'dataflow_log_' + strftime("%Y%m%d-%H%M%S") + '.txt'
        self.full_log_file = os.path.join(log_folder, log_file)
        self.log = open(self.full_log_file, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

class Logger_stderr_sherlock(object):
    '''
    for redirecting stderr to a central log file.
    note, locking did not work fir fcntl, but seems to work fine without it
    keep in mind it could be possible to get errors from not locking this
    but I haven't seen anything, and apparently linux is "atomic" or some shit...
    '''
    def __init__(self, logfile):
        self.logfile = logfile

    def write(self, message):
        with open(self.logfile, 'a+') as f:
            f.write(message)

    def flush(self):
        pass

class Printlog():
    '''
    for printing all processes into same log file on sherlock
    '''
    def __init__(self, logfile):
        self.logfile = logfile
    def print_to_log(self, message):
        with open(self.logfile, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(message)
            f.write('\n')
            fcntl.flock(f, fcntl.LOCK_UN)

def sbatch(jobname, script, modules, args, logfile, time=1, mem=1, dep=''):
    if dep != '':
        dep = '--dependency=afterok:{} --kill-on-invalid-dep=yes '.format(dep)
 
    command = f'ml {modules}; python3 {script} {json.dumps(json.dumps(args))}'

    sbatch_command = "sbatch -J {} -o ./com/%j.out -e {} -t {}:00:00 --partition=trc --open-mode=append --cpus-per-task={} --wrap='{}' {}".format(jobname, logfile, time, mem, command, dep)
    sbatch_response = subprocess.getoutput(sbatch_command)
    Printlog(logfile=logfile).print_to_log('***{}***'.format(sbatch_response))
    job_id = sbatch_response.split(' ')[-1].strip()
    return job_id

def get_job_status(job_id, logfile, should_print=False):
    printlog = getattr(Printlog(logfile=logfile), 'print_to_log')
    temp = subprocess.getoutput('sacct -n -P -j {} --noconvert --format=State,Elapsed,MaxRSS,NCPUS'.format(job_id))
    if temp == '': return None # is empty if the job is too new
    status = temp.split('\n')[0].split('|')[0]
    
    if should_print: 
        if status != 'PENDING':
            duration = temp.split('\n')[0].split('|')[1]
            num_cores = int(temp.split('\n')[0].split('|')[3])
            memory_used = float(temp.split('\n')[1].split('|')[2]) # in bytes
            core_memory = 7.77 * 1024 * 1024 * 1024 #GB to MB to KB to bytes

            if memory_used > 1024 ** 3:
                memory_to_print = f'{memory_used/1024 ** 3 :0.2f}' + 'GB'
            elif memory_used > 1024 ** 2:
                memory_to_print = f'{memory_used/1024 ** 2 :0.2f}' + 'MB'
            elif memory_used > 1024 ** 1:
                memory_to_print = f'{memory_used/1024 ** 1 :0.2f}' + 'KB'
            else:
                memory_to_print = f'{memory_used :0.2f}' + 'B'

            percent_mem = memory_used/(core_memory*num_cores)
            pretty = '*' * 20
            printlog('\n{}\nJob {} Status: {}\nDuration: {}\nNum Cores: {}\nMemory Used: {} ({:0.1f}%)\n{}\n'.format(pretty, job_id, status, duration, num_cores, memory_to_print, percent_mem, pretty))
        else:
            printlog('Job {} Status: {}'.format(job_id, status))

    return status

def wait_for_job(job_id, logfile, com_path):
    printlog = getattr(Printlog(logfile=logfile), 'print_to_log')
    printlog(f'Waiting for job {job_id}')
    while True:
        status = get_job_status(job_id, logfile)
        if status in ['COMPLETED', 'CANCELLED', 'TIMEOUT', 'FAILED', 'OUT_OF_MEMORY']:
            status = get_job_status(job_id, logfile, should_print=True)
            com_file = os.path.join(com_path, job_id + '.out')
            try:
                with open(com_file, 'r') as f:
                    output = f.read()
            except:
                output = None
            return output
        else:
            sleep(5)