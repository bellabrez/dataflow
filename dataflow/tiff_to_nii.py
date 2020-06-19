import numpy as np
import nibabel as nib
import os
from matplotlib.pyplot import imread
from xml.etree import ElementTree as ET
import sys
from tqdm import tqdm
from dataflow.utils import timing
import psutil
from PIL import Image
import time

def tiff_to_nii(xml_file):
    data_dir, _ = os.path.split(xml_file)

    tree = ET.parse(xml_file)
    root = tree.getroot()
    # Get all volumes
    sequences = root.findall('Sequence')

    # Get num channels
    num_channels = get_num_channels(sequences[0])

    # Do each channel separately (for memory reasons)
    print('Converting tiffs to nii in directory: \n{}'.format(data_dir))
    for channel in range(num_channels):
        last_num_z = None
        volumes_img = []
        for i, sequence in enumerate(sequences):
            print('{}/{}'.format(i+1, len(sequences)))
            # For a given volume, get all frames
            frames = sequence.findall('Frame')
            frames_img = []
            for frame in frames:
                # For a given frame, get filename
                files = frame.findall('File')
                filename = files[channel].get('filename')
                fullfile = os.path.join(data_dir, filename)

                # Read in file
                compress = False
                if compress:
                    starting_bit_depth = 2**13
                    desired_bit_depth = 2**8
                    im = Image.open(fullfile)
                    img = np.asarray(im)
                    img = img*(desired_bit_depth/starting_bit_depth)
                    img = img.astype('uint8')
                else:
                    img = imread(fullfile)
                frames_img.append(img)
                 
            current_num_z = np.shape(frames_img)[0]
        
            if last_num_z is not None:
                if current_num_z != last_num_z:
                    print('Inconsistent number of z-slices (scan aborted).')
                    print('Tossing last volume.')
                    break
            volumes_img.append(frames_img)
            last_num_z = current_num_z

            if i%10 == 0:
                memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
                print('Current memory usage: {:.2f}GB'.format(memory_usage))
                sys.stdout.flush()

        memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
        print('Current memory usage (pre np): {:.2f}GB'.format(memory_usage))
        sys.stdout.flush()

        volumes_img = np.asarray(volumes_img)

        memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
        print('Current memory usage (post np): {:.2f}GB'.format(memory_usage))
        sys.stdout.flush()

        # Will start as t,z,x,y. Want y,x,z,t
        volumes_img = np.moveaxis(volumes_img,1,-1) # Now t,x,y,z
        volumes_img = np.moveaxis(volumes_img,0,-1) # Now x,y,z,t
        volumes_img = np.swapaxes(volumes_img,0,1) # Now y,x,z,t

        memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
        print('Current memory usage: {:.2f}GB'.format(memory_usage))
        sys.stdout.flush()

        # If anat, will start as z,x,y (i think). Want y,x,z,
        #volumes_img = np.moveaxis(volumes_img,1,-1) # Now z,y,x
        #volumes_img = np.moveaxis(volumes_img,0,-1) # Now y,x,z
        #volumes_img = np.swapaxes(volumes_img,0,1) # Now x,y,z

        aff = np.eye(4)
        save_name = xml_file[:-4] + '_channel_{}'.format(channel+1) + '.nii'
        img = nib.Nifti1Image(volumes_img, aff)
        volumes_img = None # for memory
        print('Saving nii as {}'.format(save_name))
        img.to_filename(save_name)

def tiff_to_nii_v2(xml_file):
    aborted = False
    data_dir, _ = os.path.split(xml_file)
    print('Converting tiffs to nii in directory: \n{}'.format(data_dir))

    tree = ET.parse(xml_file)
    root = tree.getroot()
    # Get all volumes
    sequences = root.findall('Sequence')

    # Get axis dims
    num_channels = get_num_channels(sequences[0])
    num_timepoints = len(sequences)
    num_z = len(sequences[0].findall('Frame'))
    test_file = sequences[0].findall('Frame')[0].findall('File')[0].get('filename')
    fullfile = os.path.join(data_dir, test_file)
    img = imread(fullfile)
    num_y = np.shape(img)[0]
    num_x = np.shape(img)[1]
    print('num_channels: {}'.format(num_channels))
    print('num_timepoints: {}'.format(num_timepoints))
    print('num_z: {}'.format(num_z))
    print('num_y: {}'.format(num_y))
    print('num_x: {}'.format(num_x))

    # Check if bidirectional - will affect loading order
    isBidirectionalZ = sequences[0].get('bidirectionalZ')
    if isBidirectionalZ == 'True':
        isBidirectionalZ = True
    else:
        isBidirectionalZ = False
    print('BidirectionalZ is {}'.format(isBidirectionalZ))

    # loop over channels
    for channel in range(num_channels):
        last_num_z = None
        image_array = np.zeros((num_timepoints, num_z, num_y, num_x), dtype=np.uint16)
        print('Created empty array of shape {}'.format(image_array.shape))
        # loop over time
        for i, sequence in enumerate(sequences):
            print('{}/{}'.format(i+1, len(sequences)))
            # For a given volume, get all frames
            frames = sequence.findall('Frame')

            # Handle aborted scans
            current_num_z = len(frames)
            if last_num_z is not None:
                if current_num_z != last_num_z:
                    print('Inconsistent number of z-slices (scan aborted).')
                    print('Tossing last volume.')
                    aborted = True
                    break
            last_num_z = current_num_z

            # Flip frame order if a bidirectionalZ upstroke (odd i)
            if isBidirectionalZ and (i%2 != 0):
                frames = frames[::-1]
            # loop over depth (z-dim)
            for j, frame in enumerate(frames):
                # For a given frame, get filename
                files = frame.findall('File')
                filename = files[channel].get('filename')
                fullfile = os.path.join(data_dir, filename)

                # Read in file
                img = imread(fullfile)
                image_array[i,j,:,:] = img
                 
            if i%10 == 0:
                memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
                print('Current memory usage: {:.2f}GB'.format(memory_usage))
                sys.stdout.flush()

        # Will start as t,z,x,y. Want y,x,z,t
        image_array = np.moveaxis(image_array,1,-1) # Now t,x,y,z
        image_array = np.moveaxis(image_array,0,-1) # Now x,y,z,t
        image_array = np.swapaxes(image_array,0,1) # Now y,x,z,t

        # Toss last volume if aborted
        if aborted:
            image_array = image_array[:,:,:,:-1]

        memory_usage = psutil.Process(os.getpid()).memory_info().rss*10**-9
        print('Current memory usage: {:.2f}GB'.format(memory_usage))
        sys.stdout.flush()

        # If anat, will start as z,x,y (i think). Want y,x,z,
        #volumes_img = np.moveaxis(volumes_img,1,-1) # Now z,y,x
        #volumes_img = np.moveaxis(volumes_img,0,-1) # Now y,x,z
        #volumes_img = np.swapaxes(volumes_img,0,1) # Now x,y,z

        aff = np.eye(4)
        save_name = xml_file[:-4] + '_channel_{}'.format(channel+1) + '.nii'
        img = nib.Nifti1Image(image_array, aff)
        image_array = None # for memory
        print('Saving nii as {}'.format(save_name))
        img.to_filename(save_name)
        img = None # for memory
        print('Saved! sleeping for 10 sec to help memory reconfigure...')
        time.sleep(10)
        print('Sleep over')

def get_num_channels(sequence):
    frame = sequence.findall('Frame')[0]
    files = frame.findall('File')
    return len(files)

@timing
def start_convert_tiff_collections(*args):
    convert_tiff_collections(*args)

def convert_tiff_collections(directory): 
    for item in os.listdir(directory):
        new_path = directory + '/' + item

        # Check if item is a directory
        if os.path.isdir(new_path):
            convert_tiff_collections(new_path)
            
        # If the item is a file
        else:
            # If the item is an xml file
            if '.xml' in item:
                tree = ET.parse(new_path)
                root = tree.getroot()
                # If the item is an xml file with scan info
                if root.tag == 'PVScan':

                    # Also, verify that this folder doesn't already contain any .niis
                    # This is useful if rebooting the pipeline due to some error, and
                    # not wanting to take the time to re-create the already made niis
                    for item in os.listdir(directory):
                        if item.endswith('.nii'):
                            print('skipping nii containing folder: {}'.format(directory))
                            break
                    else:
                        tiff_to_nii_v2(new_path)

                    