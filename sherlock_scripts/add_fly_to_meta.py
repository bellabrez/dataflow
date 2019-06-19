import os
import sys
import json
import pandas as pd

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

def main(args):
  fly_folder = args[0]
  add_fly_to_metadata(fly_folder)

if __name__ == '__main__':
  main(sys.argv[1:])