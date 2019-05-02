import numpy as np
import nibabel as nib
import os
from matplotlib.pyplot import imread
from xml.etree import ElementTree as ET
import sys
from tqdm import tqdm
from dataflow.utils import timing

def tiff_to_nii(xml_file):
    data_dir, _ = os.path.split(xml_file)

    tree = ET.parse(xml_file)
    root = tree.getroot()
    # Get all volumes
    sequences = root.findall('Sequence')
    volumes_img = []
    print('Converting tiffs to nii in directory: \n{}'.format(data_dir))
    for sequence in tqdm(sequences):
        # For given volume, get all frames
        frames = sequence.findall('Frame')
        frames_img = []
        for frame in frames:
            # For a given frame, get all channels
            files = frame.findall('File')
            channels_img = []
            for file in files:
                filename = file.get('filename')
                fullfile = os.path.join(data_dir, filename)
                img = imread(fullfile)
                channels_img.append(img)
            frames_img.append(channels_img)
        volumes_img.append(frames_img)
        
    volumes_img = np.asarray(volumes_img)
    volumes_img = np.moveaxis(volumes_img,1,-1)
    volumes_img = np.moveaxis(volumes_img,0,-1)
    volumes_img = np.moveaxis(volumes_img,0,-1)
    volumes_img = np.swapaxes(volumes_img,0,1)

    aff = np.eye(4)
    save_name = xml_file[:-4] + '.nii'
    img = nib.Nifti1Image(volumes_img, aff)
    print('Saving nii as {}'.format(save_name))
    img.to_filename(save_name)

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
                # If the item is an xml file with scann info
                if root.tag == 'PVScan':
                    tiff_to_nii(new_path)