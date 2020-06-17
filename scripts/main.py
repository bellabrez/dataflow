import sys
import os
import warnings
import subprocess
import dataflow as flow

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.stdout = flow.Logger_stdout()
sys.stderr = flow.Logger_stderr()

target = 'G:/ftp_imports' # Where on this computer it goes
flag = '__flag__' #flag = '__flag__'
#user = 'luke' # folder to look in E: drive in Bruker
oak_target = 'X:/data/Brezovec/2P_Imaging/imports'
extensions_for_oak_transfer = ['.nii', '.csv', '.xml', 'json', 'tiff'] # needs to be 4 char
convert_to = None # Currently unsused
quit_if_local_target_exists = False

# For Bruker computer
ip ='171.65.18.54'
username = 'user'
passwd = 'flyeye'

delete_local = False

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
delete_bruker = metadata['delete_source']
email = metadata['email']
convert_to = metadata['convert_to']

try:
    transfer_stim_computer = metadata['transfer_stim_computer']
except:
    transfer_stim_computer = None

# Save email for error reporting
email_file = 'C:/Users/User/projects/dataflow/scripts/email.txt'
with open(email_file, 'w') as f:
    f.write(email)

# Strip flag of folder and join to target
full_target = target + '/' + folder.replace(flag, '')

# Send start email
flow.send_email(subject='Dataflow STARTED', message='Processing {}'.format(full_target), recipient=email)

# For Luke, pull fictrac and visual stim files from stim computer (and send to oak)
if transfer_stim_computer in ['True', 'true', 'yes']:
    print('Transfering stim computer files')
    subprocess.Popen([sys.executable, 'C:/Users/User/projects/dataflow/scripts/from_stim_computer.py'])

# Check if this folder exists ~quit capabilities~
flow.check_for_target(full_target, quit_if_local_target_exists)

# Copy from bruker computer to local computer
flow.start_copy_recursive_ftp(ftp_host, bruker_folder, full_target, ip, username, passwd)

# Confirm source and destination sizes match ~quit capabilities~
flow.confirm_bruker_transfer(ip, username, passwd, bruker_folder, full_target)

### Delete files from Bruker Computer ###
print('Delete bruker is {}'.format(delete_bruker))
if delete_bruker in ['True', 'true', 'yes']:
    flow.delete_bruker_folder(ip, username, passwd, bruker_folder)
else:
    # Strip flag from folder
    # temporarily passing on this since there is some ftp communication error for this step
    pass
    #flow.strip_bruker_flag(ip, username, passwd, bruker_folder, flag)

# Send 'transfered' email
flow.send_email(subject='Dataflow bruker transfer complete', message='Safe to turn off bruker', recipient=email)

#################################
### Convert from raw to tiffs ###
#################################

flow.convert_raw_to_tiff(full_target)

#########################################
### Convert tiff to nii or tiff stack ###
#########################################

if convert_to in ['.nii', 'nii', 'nifti']:
    flow.start_convert_tiff_collections(full_target)
elif convert_to in ['.tiff', 'tiff', '.tif', 'tif']:
    flow.convert_tiff_collections_to_stack(full_target)
else:
    print('{} is an invalid convert_to variable from metadata.'.format(convert_to))

#######################
### Transfer to Oak ###
#######################

flow.start_oak_transfer(full_target, oak_target, extensions_for_oak_transfer)

### Delete files locally
if delete_local:
    flow.delete_local(full_target)