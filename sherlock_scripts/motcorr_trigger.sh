#!/bin/bash
#SBATCH --job-name=moco_trigger
#SBATCH --partition=trc
#SBATCH --time=0:5:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --output=slurm_all.out
#SBATCH --open-mode=truncate

ml gcc/6.3.0
ml python/3.6.1
ml py-numpy/1.14.3_py36
ml py-pandas/0.23.0_py36
ml viz
ml py-scikit-learn/0.19.1_py36

#path="$1"
path="/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20190101_walking_dataset/fly_20190507-090018_52/optic"
echo "Bash - motcorr_trigger.sh started."
echo "$path"
#SBATCH --output=./outputs_motcorr_trigger/slurm-%j.out
python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/motcorr_splitter.py "$path"