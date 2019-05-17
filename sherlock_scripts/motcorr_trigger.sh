#!/bin/bash
#SBATCH --job-name=motcorr_trigger
#SBATCH --partition=trc
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

# Will create mean brain and start each partial motcorr

ml gcc/6.3.0
ml python/3.6.1
ml py-numpy/1.14.3_py36
ml py-pandas/0.23.0_py36
ml viz
ml py-scikit-learn/0.19.1_py36

path="$1"
echo "Bash - motcorr_trigger.sh started."
echo "$path"

python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/motcorr_splitter.py "$path"