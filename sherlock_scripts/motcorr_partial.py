import sys
import os
import BigBadBrain as bbb

def main(args):
	directory = args[0]
	motcorr_directory = args[1]
	master_path = args[2]
	slave_path = args[3]
	master_path_mean = args[4]
	vol_start = args[5]
	vol_end = args[6]

	master_brain = bbb.load_numpy_brain(master_path)
	slave_brain = bbb.load_numpy_brain(slave_path)
	mean_brain = bbb.load_numpy_brain(master_path_mean)

	bbb.motion_correction(master_brain,
						  slave_brain,
						  directory,
						  motcorr_directory,
						  meanbrain=mean_brain,
						  start_volume=vol_start,
						  end_volume=vol_end)

if __name__ == '__main__':
	main(sys.argv[1:])