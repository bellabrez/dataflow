import sys
import smtplib
import re
import os
import h5py
import math
from email.mime.text import MIMEText
from time import time
from time import strftime
from functools import wraps
import numpy as np
import nibabel as nib
from scipy.ndimage import imread
from xml.etree import ElementTree as ET

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