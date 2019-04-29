### Every minute:

import sys
import os
import warnings
import ftputil
import ftplib
from time import sleep
import dataflow as flow
warnings.filterwarnings("ignore",category=DeprecationWarning)

def main():
    target = 'F:\\FTP_IMPORTS' # Where on this computer it goes
    flag = '__flag__'
    user = 'luke' # folder to look in E: drive in Bruker
    ip='171.65.18.54'
    username = 'user'
    passwd = 'flyeye'

    ftp_host = flow.connect_to_ftp(ip, username, passwd)
    folder = flow.check_for_flag(ftp_host, user, flag)
    if folder is not None:
        full_target, abort_copy = flow.define_target(target, folder, flag)
        if not abort_copy:
            flow.copy_recursive_ftp(ftp_host, user + '/' + folder, full_target, ip, username, passwd)

if __name__ == "__main__":
    main()