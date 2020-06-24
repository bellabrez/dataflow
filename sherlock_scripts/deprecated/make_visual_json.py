import json
import os
import sys
import bigbadbrain as bbb    

def main():

    root_path = '/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/'
    flies = [24,25,26,27,28,29,30,31]
    for fly in flies:
        fly_folder = os.path.join(root_path, 'fly_' + str(fly))
        visual_folders = [os.path.join(fly_folder,x,'visual') for x in os.listdir(fly_folder) if 'func' in x]
        for visual_folder in visual_folders:
            if os.path.isdir(visual_folder):
                unique_stimuli = bbb.get_stimuli(visual_folder)
                with open(os.path.join(visual_folder, 'visual.json'), 'w') as f:
                    json.dump(unique_stimuli, f, indent=4)

if __name__ == '__main__':
    main()
