import os
import sys
import numpy as np
from time import strftime
from shutil import copyfile
from xml.etree import ElementTree as ET
from lxml import etree, objectify
import bigbadbrain as bbb
import pandas as pd
import json

def main():
    root_directory = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/'
    fly_folders = [os.path.join(root_directory,x) for x in os.listdir(root_directory) if 'fly' in x]
    #fly_folders = [os.path.join(root_directory, 'fly_1')]
    for fly in fly_folders:
        expt_folders = []
        expt_folders = [os.path.join(fly,x) for x in os.listdir(fly) if 'func' in x]
        if len(expt_folders) > 0:
            for expt_folder in expt_folders:
                xml_file = os.path.join(expt_folder, 'imaging', 'functional.xml')
                create_imaging_json(xml_file)

def create_imaging_json(xml_source_file):

    # Make empty dict
    source_data = {}

    # Get datetime
    datetime_str, _, _ = get_datetime_from_xml(xml_source_file)
    date = datetime_str.split('-')[0]
    time = datetime_str.split('-')[1]
    source_data['date'] = str(date)
    source_data['time'] = str(time)

    # Get rest of data
    tree = objectify.parse(xml_source_file)
    source = tree.getroot()
    statevalues = source.findall('PVStateShard')[0].findall('PVStateValue')
    for statevalue in statevalues:
        key = statevalue.get('key')
        if key == 'micronsPerPixel':
            indices = statevalue.findall('IndexedValue')
            for index in indices:
                axis = index.get('index')
                if axis == 'XAxis':
                    source_data['x_voxel_size'] = float(index.get('value'))
                elif axis == 'YAxis':
                    source_data['y_voxel_size'] = float(index.get('value'))
                elif axis == 'ZAxis':
                    source_data['z_voxel_size'] = float(index.get('value'))
        if key == 'laserPower':
            # I think this is the maximum power if set to vary by z depth
            indices = statevalue.findall('IndexedValue')
            source_data['laser_power'] = int(indices[0].get('value'))
        if key == 'pmtGain':
            indices = statevalue.findall('IndexedValue')
            for index in indices:
                index_num = index.get('index')
                if index_num == '0':
                    source_data['PMT_red'] = int(index.get('value'))
                if index_num == '1':
                    source_data['PMT_green'] = int(index.get('value'))
        if key == 'pixelsPerLine':
            source_data['x_dim'] = int(statevalue.get('value'))
        if key == 'linesPerFrame':
            source_data['y_dim'] = int(statevalue.get('value'))
    sequence = source.findall('Sequence')[0]
    last_frame = sequence.findall('Frame')[-1]
    source_data['z_dim'] = int(last_frame.get('index'))

    # Save data
    with open(os.path.join(os.path.split(xml_source_file)[0], 'scan.json'), 'w') as f:
        json.dump(source_data, f, indent=4)

def get_datetime_from_xml(xml_file):
    print('Getting datetime from {}'.format(xml_file))
    sys.stdout.flush()
    tree = ET.parse(xml_file)
    root = tree.getroot()
    datetime = root.get('date')
    # will look like "4/2/2019 4:16:03 PM" to start

    # Get dates
    date = datetime.split(' ')[0]
    month = date.split('/')[0]
    day = date.split('/')[1]
    year = date.split('/')[2]

    # Get times
    time = datetime.split(' ')[1]
    hour = time.split(':')[0]
    minute = time.split(':')[1]
    second = time.split(':')[2]

    # Convert from 12 to 24 hour time
    am_pm = datetime.split(' ')[-1]
    if am_pm == 'AM' and hour == '12':
        hour = str(00)
    elif am_pm == 'AM':
        pass
    elif am_pm == 'PM' and hour == '12':
        pass
    else:
        hour = str(int(hour) + 12)

    # Add zeros if needed
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    if len(hour) == 1:
        hour = '0' + hour

    # Combine
    datetime_str = year + month + day + '-' + hour + minute + second
    datetime_int = int(year + month + day + hour + minute + second)
    datetime_dict = {'year': year,
                     'month': month,
                     'day': day,
                     'hour': hour,
                     'minute': minute,
                     'second': second}

    return datetime_str, datetime_int, datetime_dict

if __name__ == '__main__':
    main()