### Every minute:

import ftputil
import dataflow as flow


ip = '171.65.18.54'
username = 'user'
passwd = 'flyeye'
target = '/Users/lukebrezovec/ftp_test_copy_to'

# Connect to ftp host
ftp_host = ftputil.FTPHost(ip, username, passwd)
for folder in ftp_host.listdir(''):
    if 'flag' in folder:
        copy_recursive_ftp(ftp_host, folder, target)