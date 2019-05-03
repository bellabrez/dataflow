import sys
import os
import subprocess
from dataflow.utils import timing

def convert_raw_to_tiff(full_target):
	# Start ripper watcher, which will kill bruker conversion utility when complete
	print('Starting Ripper Watcher. Will watch {}'.format(full_target))
	subprocess.Popen([sys.executable, 'C:/Users/User/projects/dataflow/scripts/ripper_killer.py', full_target])

	# Start Bruker conversion utility by calling ripper.bat 
	os.system("C:/Users/User/projects/dataflow/scripts/ripper.bat " + full_target)