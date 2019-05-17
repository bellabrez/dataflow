#!/bin/bash
#SBATCH --job-name=build_fly
#SBATCH --partition=trc
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

ml python/3.6.1

path=$(<experiment_file.txt)
echo "$path"
echo "Bash - motcorr_trigger.sh started."

python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/motcorr_splitter.py "$path"