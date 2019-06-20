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

def main(args):
    ### Move folders from imports to fly dataset - need to restructure folders ###

    flagged_directory = args[0]
    print('Building fly from directory {}'.format(flagged_directory))
    sys.stdout.flush()
    imports_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports'
    target_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/'

    # Assume this folder contains fly_1 etc
    # This folder may (or may not) contain separate areas # False, now enforcing experiment subfolders
    # Each area will have a T and a Z
    # Avoid grabbing other weird xml files, reference folder etc.
    # Need to move into fly_X folder that reflects it's date

    # Get new destination fly number by looking at last 2 char of current flies
    current_fly_number = get_new_fly_number(target_path)

    # get fly folders in flagged directory and sort to ensure correct fly order
    likely_fly_folders = os.listdir(flagged_directory)
    print('Found fly folders: {}'.format(likely_fly_folders))
    sys.stdout.flush()
    bbb.sort_nicely(likely_fly_folders)

    for likely_fly_folder in likely_fly_folders: 
        if 'fly' in likely_fly_folder:
            print('This fly will be number : {}'.format(current_fly_number))
            print('Creating fly from directory {}'.format(likely_fly_folder))
            sys.stdout.flush()

            # Define source fly directory
            source_fly = os.path.join(flagged_directory, likely_fly_folder)

            # Define destination fly directory
            fly_time = get_fly_time(source_fly)
            new_fly_folder = 'fly_' + fly_time + '_' + str(current_fly_number)
            destination_fly = os.path.join(target_path, new_fly_folder)
            os.mkdir(destination_fly)
            print('Created fly directory: {}'.format(destination_fly))
            sys.stdout.flush()

            # Copy fly data
            copy_fly(source_fly, destination_fly)

            # Add xml metadata to master pandas dataframe
            add_fly_to_metadata(destination_fly)

            # Get new fly number
            current_fly_number += 1

# Delete these remaining files

### Pull fictrac and visual from stim computer via ftp ###
def copy_fly(source_fly, destination_fly):

    ''' There will be two types of folders in a fly folder.
    1) functional folder
    2) anatomy folder
    For functional folders, need to copy fictrac and visual as well
    For anatomy folders, only copy folder. There will also be
    3) fly xml data '''

    for item in os.listdir(source_fly):
        print('Currently looking at item: {}'.format(item))
        sys.stdout.flush()
        # Handle folders
        if os.path.isdir(os.path.join(source_fly, item)):
            source_sub_folder = os.path.join(source_fly, item)
            fly_sub_folder = os.path.join(destination_fly, item)
            os.mkdir(fly_sub_folder)
            print('Created directory: {}'.format(fly_sub_folder))
            sys.stdout.flush()

            if 'anatomy' in item:
                copy_bruker_data(source_sub_folder, fly_sub_folder)
            elif 'functional' in item:
                imaging_destination = os.path.join(fly_sub_folder, 'imaging')
                os.mkdir(imaging_destination)
                copy_bruker_data(source_sub_folder, imaging_destination)
                copy_fictrac(fly_sub_folder)
                copy_visual(fly_sub_folder)

                ###################################
                ### START MOTCORR ON FUNCTIONAL ###
                ###################################
                os.system("sbatch motcorr_trigger.sh {}".format(fly_sub_folder))

            else:
                print('Invalid directory in fly folder: {}'.format(item))
                sys.stdout.flush()
        
        # Handle fly xml file for metadata management
        else:
            if item == 'fly.xml':
                print('found fly xml file')
                sys.stdout.flush()
                source_path = os.path.join(source_fly, item)
                target_path = os.path.join(destination_fly, item)
                print('Will copy from {} to {}'.format(source_path, target_path))
                sys.stdout.flush()
                copyfile(source_path, target_path)
            else:
                print('Invalid file in fly folder: {}'.format(item))
                sys.stdout.flush()

def get_expt_time(destination_region):
    # Find time of experiment based on functional.xml
    xml_file = os.path.join(destination_region, 'functional.xml')
    _, _, datetime_dict = get_datetime_from_xml(xml_file)
    true_ymd = datetime_dict['year'] + datetime_dict['month'] + datetime_dict['day']
    true_total_seconds = int(datetime_dict['hour']) * 60 * 60 + \
                         int(datetime_dict['minute']) * 60 + \
                         int(datetime_dict['second'])
    
    print('dict: {}'.format(datetime_dict))
    print('true_ymd: {}'.format(true_ymd))
    print('true_total_seconds: {}'.format(true_total_seconds))
    sys.stdout.flush()
    return true_ymd, true_total_seconds

def copy_visual(destination_region):
    visual_folder = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports/visual'
    visual_destination = os.path.join(destination_region, 'visual')

    # Find time of experiment based on functional.xml
    true_ymd, true_total_seconds = get_expt_time(os.path.join(destination_region,'imaging'))

    # Find visual folder that has the closest datetime
    # First find all folders with correct date, and about the correct time
    folders = []
    for folder in os.listdir(visual_folder):
        test_ymd = folder.split('-')[1]
        test_time = folder.split('-')[2]
        test_hour = test_time[0:2]
        test_minute = test_time[2:4]
        test_second = test_time[4:6]
        test_total_seconds = int(test_hour) * 60 * 60 + \
                             int(test_minute) * 60 + \
                             int(test_second)

        if test_ymd == true_ymd:
            time_difference = np.abs(true_total_seconds - test_total_seconds)
            if time_difference < 3 * 60:
                folders.append([folder, test_total_seconds])
                print('Found reasonable visual folder: {}'.format(folder))
    
    #if more than 1 folder, use the oldest folder
    if len(folders) == 1:
        correct_folder = folders[0]
    else:
        print('Found more than 1 visual stimulus folder within 3min of expt. Picking oldest.')
        sys.stdout.flush()
        correct_folder = folders[0] # set default to first folder
        for folder in folders:
            # look at test_total_seconds entry. If larger, call this the correct folder.
            if folder[-1] > correct_folder[-1]:
                correct_folder = folder

    # now that we have the correct folder, copy it's contents
    print('Found correct visual stimulus folder: {}'.format(correct_folder[0]))
    sys.stdout.flush()
    try:
        os.mkdir(visual_destination)
    except:
        print('{} already exists'.format(visual_destination))
    source_folder = os.path.join(visual_folder, correct_folder[0])
    print('Copying from: {}'.format(source_folder))
    sys.stdout.flush()
    for file in os.listdir(source_folder):
        target_path = os.path.join(visual_destination, file)
        source_path = os.path.join(source_folder, file)
        print('Transfering from {} to {}'.format(source_path, target_path))
        sys.stdout.flush()
        copyfile(source_path, target_path)

    ### Create json metadata
    # Update this later
    # Get unique stimuli
    stimuli, unique_stimuli = bbb.load_visual_stimuli_data(visual_destination)
    print('Unique stimuli: {}'.format(unique_stimuli))
    sys.stdout.flush()

    with open(os.path.join(visual_destination, 'visual.json'), 'w') as f:
        json.dump(unique_stimuli, f, indent=4)

def copy_fictrac(destination_region):
    fictrac_folder = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports/fictrac'
    fictrac_destination = os.path.join(destination_region, 'fictrac')

    # Find time of experiment based on functional.xml
    true_ymd, true_total_seconds = get_expt_time(os.path.join(destination_region,'imaging'))

    # Find .dat file of 1) correct-ish time, 2) correct-ish size
    datetime_correct = None
    for file in os.listdir(fictrac_folder):
        # Get datetime from file name
        datetime = datetime_from_fictrac(file)
        print('datetime: {}'.format(datetime))
        sys.stdout.flush()
        test_ymd = datetime.split('_')[0]
        test_time = datetime.split('_')[1]
        test_hour = test_time[0:2]
        test_minute = test_time[2:4]
        test_second = test_time[4:6]
        test_total_seconds = int(test_hour) * 60 * 60 + \
                             int(test_minute) * 60 + \
                             int(test_second)
        
        # Year/month/day must be exact
        if true_ymd == test_ymd:
            print('Found file from same day: {}'.format(file))
            sys.stdout.flush()
            # Must be within 3 minutes
            time_difference = np.abs(true_total_seconds - test_total_seconds)
            if time_difference < 3 * 60:
                print('Found fictrac file that matches time.')
                sys.stdout.flush()
                # Must be correct size
                if file[-4:] == '.dat':
                    fp = os.path.join(fictrac_folder, file)
                    file_size = os.path.getsize(fp)
                    if file_size > 30000000:
                        print('Found correct .dat file: {}'.format(file))
                        sys.stdout.flush()
                        datetime_correct = datetime
                        break

    if datetime_correct is None:
        print('No correct fictrac data found.')
        return

    # Now collect the 4 files with correct datetime
    print('Correct datetime: {}'.format(datetime_correct))
    sys.stdout.flush()
    correct_time_files = []
    for file in os.listdir(fictrac_folder):
        datetime = datetime_from_fictrac(file)
        #print('datetime: {}'.format(datetime))
        if datetime == datetime_correct:
            correct_time_files.append(file)

    print('Found these files with correct times: {}'.format(correct_time_files))
    sys.stdout.flush()

    # Now transfer these 4 files to the fly
    os.mkdir(fictrac_destination)
    for file in correct_time_files:
        target_path = os.path.join(fictrac_destination, file)
        source_path = os.path.join(fictrac_folder, file)
        print('Transfering {}'.format(target_path))
        sys.stdout.flush()
        copyfile(source_path, target_path)

    ### Create empty xml file.
    # Update this later
    root = etree.Element('root')
    fictrac = objectify.Element('fictrac')
    root.append(fictrac)
    objectify.deannotate(root)
    etree.cleanup_namespaces(root)
    tree = etree.ElementTree(fictrac)
    with open(os.path.join(fictrac_destination, 'fictrac.xml'), 'wb') as file:
        tree.write(file, pretty_print=True)

def datetime_from_fictrac(file):
    datetime = file.split('-')[1]
    if '.dat' in datetime or '.log' in datetime:
        datetime = datetime[:-4]
    return datetime

def copy_bruker_data(source, destination):
    # Do not update destination - download all files into that destination
    for item in os.listdir(source):
        # Create full path to item
        source_path = source + '/' + item

        # Check if item is a directory
        if os.path.isdir(source_path):
            # Do not update destination - download all files into that destination
            print('copy data is recursing.')
            sys.stdout.flush()
            copy_bruker_data(source_path, destination)
            
        # If the item is a file
        else:
            ### Change file names
            if '.nii' in item and 'TSeries' in item:
                # '_' is from channel numbers my tiff to nii adds
                item = 'functional_' + item.split('_')[1] + '_' + item.split('_')[2]
            if '.nii' in item and 'ZSeries' in item:
                item = 'anatomy_' + item.split('_')[1] + '_' + item.split('_')[2]
            if '.csv' in item:
                # Special copy for photodiode since it goes in visual folder
                item = 'photodiode.csv'
                try:
                    visual_folder = os.path.join(os.path.split(destination)[0], 'visual')
                    os.mkdir(visual_folder)
                except:
                    print('{} already exists'.format(visual_folder))
                target_path = os.path.join(os.path.split(destination)[0], 'visual', item)
                print('Transfering file {}'.format(target_path))
                sys.stdout.flush()
                copyfile(source_path, target_path)
                continue
            if '.xml' in item and 'ZSeries' in item and 'Voltage' not in item:
                item = 'anatomy.xml'
            if '.xml' in item and 'TSeries' in item and 'Voltage' not in item:
                item = 'functional.xml'
                # Use this file to create my own simplified xml
                create_imaging_json(os.path.join(source_path))
            if 'expt.xml' in item and 'anatomy' not in os.path.split(destination)[-1]:
                target_path = os.path.join(os.path.split(destination)[0], item)
                print('Transfering file {}'.format(target_path))
                sys.stdout.flush()
                copyfile(source_path, target_path)
                continue
            if 'SingleImage' in item:
                # don't copy these files
                continue
            # added this one just incase I already changed the name for some reason
            if 'functional.xml' in item or 'anatomy.xml' in item:
                create_imaging_json(os.path.join(source_path))

            target_path = destination + '/' + item
            print('Transfering file {}'.format(target_path))
            sys.stdout.flush()
            copyfile(source_path, target_path)

def create_imaging_json(xml_source_file):
    tree = objectify.parse(xml_source_file)
    source = tree.getroot()
    
    # Get data
    source_data {}
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
            source_data['laser_power'] = indices[0].get('value')
        if key == 'pmtGain':
            indices = statevalue.findall('IndexedValue')
            for index in indices:
                index_num = index.get('index')
                if index_num == '0':
                    source_data['PMT_red'] = index.get('value')
                if index_num == '1':
                    source_data['PMT_green'] = index.get('value')

    # Save data
    with open(os.path.join(os.path.split(xml_source_file)[0], 'scan.json'), 'w') as f:
        json.dump(source_data, f, indent=4)

def get_fly_time(fly_folder):
    # need to read all xml files and pick oldest time
    # find all xml files
    xml_files = []
    xml_files = get_xml_files(fly_folder, xml_files)
    

    print('found xml files: {}'.format(xml_files))
    sys.stdout.flush()
    datetimes_str = []
    datetimes_int = []
    for xml_file in xml_files:
        datetime_str, datetime_int, _ = get_datetime_from_xml(xml_file)
        datetimes_str.append(datetime_str)
        datetimes_int.append(datetime_int)

    # Now pick the oldest datetime
    datetimes_int = np.asarray(datetimes_int)
    print('Found datetimes: {}'.format(datetimes_str))
    sys.stdout.flush()
    index_min = np.argmin(datetimes_int)
    datetime = datetimes_str[index_min]
    print('Found oldest datetime: {}'.format(datetime))
    sys.stdout.flush()
    return datetime

def get_xml_files(fly_folder, xml_files):
    # Look at items in fly folder
    for item in os.listdir(fly_folder):
        full_path = os.path.join(fly_folder, item)
        if os.path.isdir(full_path):
            xml_files = get_xml_files(full_path, xml_files)
        else:
            if '.xml' in item and \
            '_Cycle' not in item and \
            'fly.xml' not in item and \
            'scan.xml' not in item and \
            'expt.xml' not in item:
                xml_files.append(full_path)
                print('Found xml file: {}'.format(full_path))
                sys.stdout.flush()
    return xml_files

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

def get_new_fly_number(target_path):
    oldest_fly = 0
    for current_fly_folder in os.listdir(target_path):
        if 'fly' in current_fly_folder and current_fly_folder[-3] == '_':
            last_2_chars = current_fly_folder[-2:]
            if int(last_2_chars) > oldest_fly:
                oldest_fly = int(last_2_chars)
    current_fly_number = oldest_fly + 1
    return current_fly_number

def load_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
    return data

def add_fly_to_metadata(fly_folder):
    # For each fly, need to handle multiple experiments
    
    # Load fly metadata
    fly_file = os.path.join(fly_folder, 'fly.json')
    fly_data = load_json(fly_file)
    
    # Add each experiment
    for item in os.listdir(fly_folder):
        if 'func' in item:
            expt_folder = os.path.join(fly_folder, item)
            add_expt_to_metadata(fly_data, expt_folder)

def add_expt_to_metadata(fly_data, expt_folder):    
    # Load expt metadata
    expt_file = os.path.join(expt_folder, 'expt.json')
    expt_data = load_json(expt_file)
    
    # Load scan metadata
    scan_file = os.path.join(expt_folder, 'imaging', 'scan.json')
    scan_data = load_json(scan_file)

    # Load visual metadata
    try:
        visual_file = os.path.join(expt_folder, 'visual', 'visual.json')
        visual_data = load_json(visual_file)
    except:
        visual_data = None
        print('Visual metadata not found.')
        sys.stdout.flush()
    
    fictrac_data = None
    # Load fictrac metadata
    # try:
    #     xml_file = os.path.join(expt_folder, 'fictrac', 'fictrac.xml')
    #     fictrac = load_xml(xml_file)
        
    #     # UPDATE THIS WHEN FICTRAC META CONTAINS REAL INFO
    #     fictrac = True
    # except:
    #     fictrac = None
    #     print('Fictrac metadata not found.')
    #     sys.stdout.flush()
    
    # Load experiment master dataframe
    master_expt_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/master_expt.pkl'
    master_expt = pd.read_pickle(master_expt_path)
    
    # Get fly_id
    fly_folder = os.path.split(os.path.split(expt_folder)[0])[-1]
    fly_id = fly_folder.split('_')[-1]

    # Get expt_id
    expt_id = expt_folder.split('_')[-1]

    # Append the new row
    new_row = {'fly_id': fly_id,
               'expt_id': expt_id,
               'date': fly_data['date'],
               'time': expt_data['time'],
               'circ_on': fly_data['circadian_on'],
               'circ_off': fly_data['circadian_off'],
               'gender': fly_data['gender'],
               'age': fly_data['age'],
               'genotype': fly_data['genotype'],
               'brain_area': expt_data['brain_area'],
               'expt_notes': expt_data['notes'],
               'temp': fly_data['temp'],
               'fly_notes': fly_data['notes'],
               'laser_power': scan_data['power'],
               'PMT_green': scan_data['PMT_green'],
               'PMT_red': scan_data['PMT_red'],
               'x_voxel_size': scan_data['x_voxel_size'],
               'y_voxel_size': scan_data['y_voxel_size'],
               'z_voxel_size': scan_data['z_voxel_size']}
    
    if visual_data is not None:
        new_row['visual_stimuli'] = visual_data
    if fictrac_data is not None:
        new_row['fictrac'] = fictrac
               
    master_expt = master_expt.append(new_row, ignore_index=True)
    
    # Save
    master_expt.to_pickle(master_expt_path)

def load_xml(file):
    tree = objectify.parse(file)
    root = tree.getroot()
    return root

if __name__ == '__main__':
    main(sys.argv[1:])