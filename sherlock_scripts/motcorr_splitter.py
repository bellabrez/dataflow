import os
import sys
import bigbadbrain as bbb
import subprocess
import numpy as np

def main(args):
    '''
    Lets write this asssuming there are files:
    functional_channel_1.nii, serving as red master
    functional_channel_2.nii, serving as green slave
    '''
    path = args[0]

    ### Create mean brain
    master_brain_path = os.path.join(path, 'functional_channel_1.nii')
    slave_brain_path = os.path.join(path, 'functional_channel_2.nii')
    master_brain = bbb.load_numpy_brain(master_brain_path)
    master_brain_mean = bbb.make_meanbrain(master_brain)
    master_brain_mean_file = os.path.join(path, 'functional_channel_1_mean.nii')
    bbb.save_brain(master_brain_mean_file, master_brain_mean)
    print('Saved mean brain {}'.format(master_brain_mean_file))

    ### Make subfolder if it doesn't exist
    subfolder = 'motcorr'
    motcorr_directory = os.path.join(path, subfolder)
    if not os.path.exists(motcorr_directory):
        os.makedirs(motcorr_directory)

    # How many volumes?
    num_vols = np.shape(master_brain)[-1]

    #Start fleet of motcorr_partial.sh, giving each the correct portion of data

    num_vols = 100 ###### FOR TESTING; REMOVE. ######
    for i in range(0,num_vols,100):
        vol_start = i
        vol_end = i + 100

        # handle last section
        if vol_end > num_vols:
            vol_end = num_vols

        ### SUBMIT JOB ###
        jobid = subprocess.check_output('sbatch motcorr_partial.sh {} {} {} {} {} {} {}'.format(
            path,
            motcorr_directory,
            master_brain_path,
            slave_brain_path,
            master_brain_mean_file,
            vol_start,
            vol_end),
            shell=True)
        jobid_str = jobid.decode('utf-8')
        print('jobid: {}'.format(jobid_str))

    # extract jobids

    # start motcorr_stitcher.sh with dependences on all jobs above finishing

    #os.system("sbatch motcorr_partial.sh {} {} {} {} {} {} {}".format(p

if __name__ == '__main__':
    main(sys.argv[1:])