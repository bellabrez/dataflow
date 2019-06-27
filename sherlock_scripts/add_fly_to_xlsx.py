from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Font, Fill
import json
import os

def load_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
    return data

filename='/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/master_2P.xlsx'
wb = load_workbook(filename=filename, read_only=False)
ws = wb.active
#ws = wb['big_data']
#wb = Workbook()
#wb = wb.load()
# grab the active worksheet
#col = ws.column_dimensions['B']
#col.font = Font(bold=True)
# Data can be assigned directly to cells
#ws['A1'] = 42

# Rows can also be appended
fly_folder = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/fly_1'
fly_file = os.path.join(fly_folder, 'fly.json')
fly_data = load_json(fly_file)

expt_file = os.path.join(fly_folder, 'func_0', 'expt.json')
expt_data = load_json(expt_file)

scan_file = os.path.join(fly_folder, 'func_0', 'imaging', 'scan.json')
scan_data = load_json(scan_file)

# Get fly_id
fly_folder = os.path.split(os.path.split(expt_folder)[0])[-1]
fly_id = fly_folder.split('_')[-1]

# Get expt_id
expt_id = expt_folder.split('_')[-1]

# Append the new row
new_row = [fly_id,
           expt_id,
           fly_data['date'],
           expt_data['brain_area'],
           fly_data['genotype'],
           0,
           fly_data['notes'],
           expt_data['notes'],
           expt_data['time'],
           fly_data['circadian_on'],
           fly_data['circadian_off'],
           fly_data['gender'],
           fly_data['age'],
           fly_data['temp'],
           scan_data['power'],
           scan_data['PMT_green'],
           scan_data['PMT_red'],
           scan_data['x_dim'],
           scan_data['y_dim'],
           scan_data['z_dim'],
           scan_data['x_voxel_size'],
           scan_data['y_voxel_size'],
           scan_data['z_voxel_size']]

#if visual_data is not None:
#    new_row['visual_stimuli'] = visual_data
#if fictrac_data is not None:
#    new_row['fictrac'] = fictrac

ws.append(new_row)

# Save the file
filename='/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/master_2P_new.xlsx'
wb.save(filename)

