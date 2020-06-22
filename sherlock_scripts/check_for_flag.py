import os
import sys
import json
import bigbadbrain as bbb
from time import sleep
import datetime

def main(args):

    logfile = args['logfile']
    imports_path = args['imports_path']
    printlog = getattr(flow.Printlog(logfile=logfile), 'print_to_log')

    printlog('Checking build queue.')
    printlog('Time: {}'.format(datetime.datetime.now()))

    queued_folders = []
    for item in os.listdir(imports_path):
        printlog('Found queued folder {}'.format(item))
        queued_folders.append(item)

    if len(queued_folders) == 0:
        printlog('No queued folders found. Raising SystemExit.')
        raise SystemExit
    else:
        bbb.sort_nicely(queued_folders)
        folder_to_build = os.path.join(os.path.split(imports_path)[0], queued_folders[0])
        print(folder_to_build)
        printlog('Commencing processing of: {}'.format(folder_to_build))
        #os.system('sbatch build_fly.sh {}'.format(folder_to_build))
        #os.remove(os.path.join(imports_path, queued_folders[0]))

if __name__ == '__main__':
    #main(sys.argv[1:])
    main(json.loads(sys.argv[1]))