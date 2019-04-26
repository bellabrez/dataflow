### Every minute:

import ftputil
import dataflow as flow


ip = '171.65.18.54'
username = 'user'
passwd = 'flyeye'
target = 'F:/FTP_IMPORTS'

# Connect to ftp host
ftp_host = ftputil.FTPHost(ip, username, passwd)
for folder in ftp_host.listdir(''):
    if 'rip' in folder:
        flow.copy_recursive_ftp(ftp_host, folder, target)