import os
import sys
import bigbadbrain as bbb
import dataflow as flow
import numpy as np
import re
import json
import nibabel as nib

def main(args):

    logfile = args['logfile']
    directory = args['directory'] # moco full path
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')
    printlog('\nStitcher started for {}'.format(directory))

    ######################
    ### Get file names ###
    ######################

    colors = ['red', 'green']
    files = {}
    for color in colors:
        files[color] = []
        for file in os.listdir(directory):
            if '.nii' in file and color in file:
                files[color].append(os.path.join(directory, file))
        bbb.sort_nicely(files[color])

    #####################
    ### Stitch brains ###
    #####################

    for color in colors:
        if len(files[color]) > 0:
            brains = []
            for brain_file in files[color]:
                brain = np.asarray(nib.load(brain_file).get_data(), dtype=np.uint16)
                #brain = bbb.load_numpy_brain(brain_file)

                # Handle edgecase of single volume brain
                if len(np.shape(brain)) == 3:
                    brain = brain[:,:,:,np.newaxis]
                #print('shape of partial brain: {}'.format(np.shape(brain)))
                brains.append(brain)

            #print('brains len: {}'.format(len(brains)))
            stitched_brain = np.concatenate(brains, axis=-1)
            printlog('Stitched brain shape: {}'.format(np.shape(stitched_brain)))
            #bbb.save_brain(save_file, stitched_brain)

            save_file = os.path.join(directory, 'stitched_brain_{}.nii'.format(color))
            aff = np.eye(4)
            img = nib.Nifti1Image(stitched_brain, aff)
            img.to_filename(save_file)
            stitched_brain = None

            # delete partial brains
            [os.remove(file) for file in files[color]]

    ##########################
    ### Stitch moco params ###
    ##########################

    motcorr_param_files = []
    for item in os.listdir(directory):
        if '.npy' in item:
            file = os.path.join(directory, item)
            motcorr_param_files.append(file)
    bbb.sort_nicely(motcorr_param_files)
    
    motcorr_params = []
    for file in motcorr_param_files:
        motcorr_params.append(np.load(file))

    if len(motcorr_params) > 0:
        stitched_params = np.concatenate(motcorr_params, axis=0)
        save_file = os.path.join(directory, 'motcorr_params_stitched')
        np.save(save_file, stitched_params)
        [os.remove(file) for file in motcorr_param_files]
        xml_dir = os.path.join(os.path.split(directory)[0], 'imaging')
        #print('directory: {}'.format(directory))
        #print('xml_dir: {}'.format(xml_dir))
        #sys.stdout.flush()
        bbb.save_motion_figure(stitched_params, xml_dir, directory)
    else:
        printlog('Empty motcorr params - skipping saving moco figure.')

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))