import sys
import os
import warnings
import dataflow as flow

warnings.filterwarnings("ignore",category=DeprecationWarning)
sys.stdout = flow.Logger_stdout()
sys.stderr = flow.Logger_stderr()

target = 'F:/FTP_IMPORTS' # Where on this computer it goes
flag = '__flag__' #flag = '__flag__'
user = 'luke' # folder to look in E: drive in Bruker
ip='171.65.18.54'
username = 'user'
passwd = 'flyeye'
oak_target = 'X:/data/Brezovec/2P_Imaging/imports'
extensions_for_oak_transfer = ['.nii', '.csv', '.xml']
convert_to = '.nii' # Currently unsused
quit_if_local_target_exists = False

delete_bruker = True # Currently unused
delete_local = True
delete_oak = False

##################################
### Transfer files from Bruker ###
##################################

# Connect via ftp
ftp_host = flow.connect_to_ftp(ip, username, passwd)

# Check if any folders have flag ~quit capabilities~
folder, metadata, user = flow.check_for_flag(ftp_host, flag)
bruker_folder = user + '/' + folder

# Overwrite default variables based on loaded metadata
oak_target = metadata['oak_target']
#delete_bruker = metadata['delete_source']
#convert_to = metadata['convert_to']
email = metadata['email']

# Strip flag of folder and join to target
full_target = target + '/' + folder.replace(flag, '')

# Send start email
flow.send_email(subject='Dataflow STARTED', message='Processing {}'.format(full_target), recipient=email)

# Check if this folder exists ~quit capabilities~
flow.check_for_target(full_target, quit_if_local_target_exists)

# Copy from bruker computer to local computer
flow.start_copy_recursive_ftp(ftp_host, bruker_folder, full_target, ip, username, passwd)

# Confirm source and destination sizes match ~quit capabilities~
flow.confirm_bruker_transfer(ip, username, passwd, bruker_folder, full_target)

### Delete files from Bruker Computer ###
if delete_bruker:
    flow.delete_bruker_folder(ip, username, passwd, bruker_folder)

# Send 'transfered' email
flow.send_email(subject='Dataflow bruker transfer complete', message='Safe to turn off bruker', recipient=email)

#################################
### Convert from raw to tiffs ###
#################################

flow.convert_raw_to_tiff(full_target)

###########################
### Convert tiff to nii ###
###########################

flow.start_convert_tiff_collections(full_target)

#######################
### Transfer to Oak ###
#######################

flow.start_oak_transfer(full_target, oak_target, extensions_for_oak_transfer)

### Delete files locally
if delete_local:
    flow.delete_local(full_target)

### Notify user via email ###
flow.send_email(subject='Dataflow SUCCESS',
                message='Processed {}\nProcessed files located at {}'.format(full_target, oak_target),
                recipient=email)