import os
import sys
#import BigBadBrain as bbb

def main(args):
    '''
    Lets write this asssuming there are files:
    functional_channel_1.nii, serving as red master
    functional_channel_2.nii, serving as green slave
    '''
    path = args[0]

    ### Create mean brain
    #master_brain_path = os.path.join(path, 'functional_channel_1.nii')
    #slave_brain_path = os.path.join(path, 'functional_channel_2.nii')
    #master_brain = bbb.load_numpy_brain(master_brain_path)
    #master_brain_mean = bbb.make_meanbrain(master_brain)
    #save_file = os.path.join(path, 'functional_channel_1_mean.nii')
    #bbb.save_brain(save_file, master_brain_mean)

    #Start 10 motcorr_partial.sh, giving each the correct portion of data
    os.system("sbatch motcorr_partial.sh {}".format(path))
    # 





if __name__ == '__main__':
    main(sys.argv[1:])