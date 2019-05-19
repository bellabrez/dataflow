import os
import sys
import bigbadbrain as bbb
import subprocess

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

    #Start 10 motcorr_partial.sh, giving each the correct portion of data
    for i in [0,10]:
        vol_start = 0 + i
        vol_end = 5 + i
        jobid = subprocess.check_output('sbatch motcorr_partial.sh {} {} {} {} {} {} {}'.format(
            path,
            motcorr_directory,
            master_brain_path,
            slave_brain_path,
            master_brain_mean_file,
            vol_start, vol_end),
            shell=True)
        print('jobid: {}'.format(jobid))

    #os.system("sbatch motcorr_partial.sh {} {} {} {} {} {} {}".format(p

if __name__ == '__main__':
    main(sys.argv[1:])