import sys
import os
import warnings
import ftputil
from datetime import datetime
import dataflow as flow

ip ='171.65.17.246'
username = 'clandininlab'
passwd = 'jointhelab@'
fictrac_target = 'G:/ftp_imports/fictrac'
fictrac_source = 'fictrac/bin'
allowable_extensions = ['.log', '.avi', '.dat']

visual_source = 'luke_data'
visual_target = 'G:/ftp_imports/visual'

oak_target = 'X:/data/Brezovec/2P_Imaging/imports'

def main():
    print('Starting download of fictrac and visual stim files.')
    ftp_host = ftputil.FTPHost(ip, username, passwd)
    all_fictrac_files = ftp_host.listdir(fictrac_source)
    # of the form:
    #fictrac-20181116_172030.log
    #fictrac-20181116_172038-debug.avi
    #fictrac-20181116_172038-raw.avi
    #fictrac-20181116_172030.dat

    # Should download all fictrac files
    # today = datetime.today().strftime('%Y%m%d')

    for file in all_fictrac_files:
        if file[-4:] in allowable_extensions:
            target_path = fictrac_target + '/' + file
            source_path = fictrac_source + '/' + file
            if os.path.isfile(target_path):
                print('File already exists. Skipping.  {}'.format(target_path))
            else:
                print('Downloading {}'.format(target_path))
                ftp_host.download(source_path, target_path)

    # Copy from visual
    flow.start_copy_recursive_ftp(ftp_host, visual_source, visual_target, ip, username, passwd)

    # Send fictrac files to oak
    flow.start_oak_transfer(fictrac_target, oak_target, allowable_extensions=None, add_flag=False)

    # Send visual files to oak
    flow.start_oak_transfer(visual_target, oak_target, allowable_extensions=None, add_flag=False)

    print('Finished upload of fictrac and visual stim files to oak.')

if __name__ == '__main__':
    main()