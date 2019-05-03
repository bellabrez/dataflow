import dataflow as flow
import os
import glob

log_folder = 'C:/Users/User/Desktop/dataflow_logs/*'
list_of_files = glob.glob(log_folder) # * means all if need specific format then *.csv
lastest_file = max(list_of_files, key=os.path.getctime)

with open(lastest_file, 'r') as f:
	log_info = f.read()

flow.send_email(subject='dataflow', message=log_info, recipient="brezovec@stanford.edu")