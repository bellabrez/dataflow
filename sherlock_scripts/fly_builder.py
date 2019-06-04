import os
import sys
import numpy as np
from time import strftime
from shutil import copyfile
from xml.etree import ElementTree as ET
import bigbadbrain as bbb

def main(args):
    ### Move folders from imports to fly dataset - need to restructure folders ###

    flagged_directory = args[0]
    print('Building fly from directory {}'.format(flagged_directory))
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
    bbb.sort_nicely(likely_fly_folders)

    for likely_fly_folder in likely_fly_folders: 
        if 'fly' in likely_fly_folder:
            print('This fly will be number : {}'.format(current_fly_number))
            print('Creating fly from directory {}'.format(likely_fly_folder))

            # Define source fly directory
            source_fly = os.path.join(flagged_directory, likely_fly_folder)

            # Define destination fly directory
            fly_time = get_fly_time(source_fly)
            new_fly_folder = 'fly_' + fly_time + '_' + str(current_fly_number)
            destination_fly = os.path.join(target_path, new_fly_folder)
            os.mkdir(destination_fly)
            print('Created fly directory: {}'.format(destination_fly))

            # Copy fly data
            copy_fly(source_fly, destination_fly)

            # Get new fly number
            current_fly_number += 1

# Delete these remaining files

### Pull fictrac and visual from stim computer via ftp ###
def copy_fly(source_fly, destination_fly):
    # Check if the source fly has folders for brain areas:
    # Switching to assuming there are brain regions!!!
    #has_brain_regions = True
    #for item in os.listdir(source_fly):
    #    full_item = os.path.join(source_fly, item)
    #    # If any items are not directories, must not contain brain regions.
    #    if 'TSeries' in full_item or 'ZSeries' in full_item:
    #        has_brain_regions = False

    #print('Has brain regions: {}'.format(has_brain_regions))

    # If brain regions, copy files for each region
    # if has_brain_regions:
    # Assuming flies contain region folders
    for region in os.listdir(source_fly):
        source_region = os.path.join(source_fly, region)
        destination_region = os.path.join(destination_fly, region)
        os.mkdir(destination_region)
        print('Created region directory: {}'.format(destination_region))
        copy_bruker_data(source_region, destination_region)
        copy_fictrac(destination_region)

        ###################################
        ### START MOTCORR ON EXPERIMENT ###
        ###################################
        os.system("sbatch motcorr_trigger.sh {}".format(destination_region))

def copy_fictrac(destination_region):
    fictrac_folder = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/imports/fictrac'
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


    # Find .dat file of 1) correct-ish time, 2) correct-ish size
    for file in os.listdir(fictrac_folder):
        # Get datetime from file name
        datetime = datetime_from_fictrac(file)
        print('datetime: {}'.format(datetime))
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
            # Must be within 3 minutes
            time_difference = np.abs(true_total_seconds - test_total_seconds)
            if time_difference < 3 * 60:
                print('Found fictrac file that matches time.')
                # Must be correct size
                if file[-4:] == '.dat':
                    fp = os.path.join(fictrac_folder, file)
                    file_size = os.path.getsize(fp)
                    if file_size > 30000000:
                        print('Found correct .dat file: {}'.format(file))
                        datetime_correct = datetime
                        break

    # Now collect the 4 files with correct datetime
    print('Correct datetime: {}'.format(datetime_correct))
    correct_time_files = []
    for file in os.listdir(fictrac_folder):
        datetime = datetime_from_fictrac(file)
        #print('datetime: {}'.format(datetime))
        if datetime == datetime_correct:
            correct_time_files.append(file)

    print('Found these files with correct times: {}'.format(correct_time_files))

    # Now transfer these 4 files to the fly
    for file in correct_time_files:
        target_path = os.path.join(destination_region, file)
        source_path = os.path.join(fictrac_folder, file)
        print('Transfering {}'.format(target_path))
        copyfile(source_path, target_path)

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
                item = 'photodiode.csv'
            if '.xml' in item and 'ZSeries' in item and 'Voltage' not in item:
                item = 'anatomy.xml'
            if '.xml' in item and 'TSeries' in item and 'Voltage' not in item:
                item = 'functional.xml'

            target_path = destination + '/' + item
            print('Transfering file {}'.format(target_path))

            copyfile(source_path, target_path)

def get_fly_time(fly_folder):
    # need to read all xml files and pick oldest time
    # find all xml files
    xml_files = []
    xml_files = get_xml_files(fly_folder, xml_files)
    print('found xml files: {}'.format(xml_files))
    datetimes_str = []
    datetimes_int = []
    for xml_file in xml_files:
        datetime_str, datetime_int, _ = get_datetime_from_xml(xml_file)
        datetimes_str.append(datetime_str)
        datetimes_int.append(datetime_int)

    # Now pick the oldest datetime
    datetimes_int = np.asarray(datetimes_int)
    print('Found datetimes: {}'.format(datetimes_str))
    index_min = np.argmin(datetimes_int)
    datetime = datetimes_str[index_min]
    print('Found oldest datetime: {}'.format(datetime))
    return datetime

def get_xml_files(fly_folder, xml_files):
    # Look at items in fly folder
    for item in os.listdir(fly_folder):
        full_path = os.path.join(fly_folder, item)
        if os.path.isdir(full_path):
            xml_files = get_xml_files(full_path, xml_files)
        else:
            if '.xml' in item and '_Cycle' not in item:
                xml_files.append(full_path)
                print('Found xml file: {}'.format(full_path))
    return xml_files

def get_datetime_from_xml(xml_file):
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

if __name__ == '__main__':
    main(sys.argv[1:])