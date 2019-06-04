#!/bin/bash
#SBATCH --job-name=moco_stitcher
#SBATCH --partition=trc
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --output=slurm_moco.out
#SBATCH --open-mode=append

ml gcc/6.3.0
ml python/3.6.1
ml py-numpy/1.14.3_py36
ml py-pandas/0.23.0_py36
ml viz
ml py-scikit-learn/0.19.1_py36

directory="$1"

python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/motcorr_stitcher.py "$directory"