#!/bin/bash
#SBATCH --job-name=moco_partial
#SBATCH --partition=trc
#SBATCH --time=0:5:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=slurm_all.out
#SBATCH --open-mode=append

ml gcc/6.3.0
ml python/3.6.1
ml py-numpy/1.14.3_py36
ml py-pandas/0.23.0_py36
ml viz
ml py-scikit-learn/0.19.1_py36

directory="$1"
motcorr_directory="$2"
master_path="$3"
slave_path="$4"
master_path_mean="$5"
vol_start="$6"
vol_end="$7"
#SBATCH --output=./outputs_motcorr_partial/slurm-%j.out

python3 -W ignore /home/users/brezovec/projects/dataflow/sherlock_scripts/motcorr_partial.py "$directory" "$motcorr_directory" "$master_path" "$slave_path" "$master_path_mean" "$vol_start" "$vol_end"