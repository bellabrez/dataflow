import os
import sys
from time import strftime
from shutil import copyfile
from xml.etree import ElementTree as ET

def main():
    ### Move folders from imports to fly dataset - need to restructure folders ###
    imports_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/IMPORTS'
    target_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/'
    done_flag = '__done__'

    # Will look for and get folder that contains __done__
    flagged_directory = check_for_done_flag(imports_path, done_flag)

    # Assume this folder contains fly_1 etc
    # This folder may (or may not) contain separate areas
    # Each area will have a T and a Z
    # Avoid grabbing other weird xml files, reference folder etc.
    # Need to move into fly_X folder that reflects it's date

    # Get new destination fly number by looking at last 2 char of current flies
    current_fly_number = get_new_fly_number(target_path)

    for likely_fly_folder in os.listdir(flagged_directory): #NEED TO SORT THESE FLIES BY NUMBER
        if 'fly' in likely_fly_folder:
            print('This fly will be number : {}'.format(current_fly_number))

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
    has_brain_regions = True
    for item in os.listdir(source_fly):
        full_item = os.path.join(source_fly, item)
        # If any items are not directories, must not contain brain regions.
        if os.isfile(full_item):
            has_brain_regions = False

    # If brain regions, copy files for each region
    if has_brain_regions:
        for region in os.listdir(source_fly):
            source_region = os.path.join(source_fly, region)
            destination_region = os.path.join(destination_fly, region)
            os.mkdir(destination_region)
            print('Created region directory: {}'.format(destination_region))
            copy_data(source_region, destination_region)

    # Else just copy the one fly folder
    else:
        copy_data(source_fly, destination_fly)

def copy_data(source, destination):
    for item in os.listdir(source):
        source_path = os.path.join(source, item)
        target_path = os.path.join(destination, item)

        # Exclude directories (avoids reference directory etc.).
        if os.isfile(source_path):
            # CAN ADD OTHER FILTERS HERE
            print('Transfering file {}'.format(target_path))
            copyfile(source_path, target_path)

def get_fly_time(fly_folder):
    # need to read all xml files and pick oldest time
    # find all xml files
    xml_files = get_xml_files(fly_folder)
    datetimes = []
    for xml_file in xml_files:
        datetimes.append(get_datetime_from_xml(xml_file))

    # Now pick the oldest datetime
    datetimes = np.asarray(datetimes)
    print('Found datetimes: {}'.format(datetimes))
    datetime = np.min(datetimes)
    print('Found oldest datetime: {}'.format(datetime))
    return datetime

def get_xml_files(fly_folder):
    xml_files = []
    # Look at items in fly folder
    for item in os.listdir(fly_folder):
        item_path = os.path.join(fly_folder, item)

        # If this item is a directory, it is a region directory
        if os.isdir(item_path):
            region_folder = os.path.join(fly_folder, item_path)

            # Look at items in fly region folder if they exist
            for sub_item in os.listdir(region_folder):
                sub_item_path = os.path.join(region_folder, sub_item)
                if '.xml' in sub_item:
                    xml_files.append(sub_item_path)
        else:
            if '.xml' in item:
                xml_files.append(item_path)
                print('Found xml file: {}'.format(item_path))
    return xml_files

def get_datetime_from_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    datetime = root['date']
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

    # Combine
    datetime_new = year + month + day + '-' + hour + minute + second
    return datetime_new

def get_new_fly_number(target_path):
    oldest_fly = 0
    for current_fly_folder in os.listdir(target_path):
        if 'fly' in current_fly_folder and current_fly_folder[-3] == '_':
            last_2_chars = current_fly_folder[-2:]
            if int(last_2_chars) > oldest_fly:
                oldest_fly = int(last_2_chars)
    current_fly_number = oldest_fly + 1
    return current_fly_number

def check_for_done_flag(imports_path, done_flag):
    for item in os.listdir(imports_path):
        if done_flag in item:
            print('Found flagged directory {}'.format(item))
            item_path = os.path.join(imports_path, item)
            return item_path
    raise SystemExit

if __name__ == '__main__':
    main()
