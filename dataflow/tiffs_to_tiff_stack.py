from xml.etree import ElementTree as ET
import os
import sys
import glob
from skimage.external import tifffile

def convert_tiff_collections_to_stack(directory):
    for item in os.listdir(directory):
        new_path = directory + '/' + item

        # Check if item is a directory
        if os.path.isdir(new_path):
            convert_tiff_collections_to_stack(new_path)
            
        # If the item is a file
        else:
            # If the item is an xml file
            if '.xml' in item:
                tree = ET.parse(new_path)
                root = tree.getroot()
                # If the item is an xml file with scan info
                if root.tag == 'PVScan':
                    tiffs_to_stack(directory)

def tiffs_to_stack(directory):
    if not directory[-1] == '/':
        directory = directory + '/'
    stack_fn = os.path.join(directory, 'stack.tiff')
    print('Creating tiff stack from {}'.format(directory))
    with tifffile.TiffWriter(stack_fn) as stack:
        for filename in sorted(glob.glob(directory + '*.tif')):
            stack.save(tifffile.imread(filename))
