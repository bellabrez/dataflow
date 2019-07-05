import os
import sys
import bigbadbrain as bbb
import subprocess
import numpy as np
import time

def main(args):
    '''
    Lets write this asssuming there are files:
    functional_channel_1.nii, serving as red master
    functional_channel_2.nii, serving as green slave
    '''
    path = args[0]

    ### Create mean brain
    imaging_path = os.path.join(path, 'imaging')
    master_brain_path = os.path.join(imaging_path, 'functional_channel_1.nii')
    slave_brain_path = os.path.join(imaging_path, 'functional_channel_2.nii')
    print('Using master brain {}'.format(master_brain_path))
    master_brain = bbb.load_numpy_brain(master_brain_path)
    master_brain_mean = bbb.make_meanbrain(master_brain)
    master_brain_mean_file = os.path.join(imaging_path, 'functional_channel_1_mean.nii')
    bbb.save_brain(master_brain_mean_file, master_brain_mean)
    print('Saved mean brain {}'.format(master_brain_mean_file))

    # How many volumes?
    num_vols = np.shape(master_brain)[-1]

    # Clear memory
    master_brain = None
    master_brain_mean = None
    time.sleep(5)


    ### Make subfolder if it doesn't exist
    subfolder = 'motcorr'
    motcorr_directory = os.path.join(path, subfolder)
    if not os.path.exists(motcorr_directory):
        os.makedirs(motcorr_directory)


    ### Start fleet of motcorr_partial.sh, giving each the correct portion of data

    #num_vols = 5 can do this to test
    step = 100 # can reduce this for testing
    job_ids = []
    for i in range(0,num_vols,step):
        vol_start = i
        vol_end = i + step

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

        # Get job ids so we can use them as dependencies
        jobid_str = jobid.decode('utf-8')
        jobid_str = [x for x in jobid_str.split() if x.isdigit()][0]
        print('jobid: {}'.format(jobid_str))
        job_ids.append(jobid_str)

    ### Start motcorr_stitcher.sh with dependences on all jobs above finishing ###
    # Create weird job string slurm wants
    job_ids_colons = ':'.join(job_ids)
    print('Colons: {}'.format(job_ids_colons))
    os.system('sbatch --dependency=afterany:{} motcorr_stitcher.sh {}'.format(job_ids_colons, motcorr_directory))

if __name__ == '__main__':
    main(sys.argv[1:])