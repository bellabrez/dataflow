#!/bin/bash
#SBATCH --job-name=flag_check
#SBATCH --partition=trc
#SBATCH --time=0:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=./outputs_check_for_flag/slurm-%j.out

ml gcc/6.3.0
ml python/3.6.1
ml py-numpy/1.14.3_py36
ml py-pandas/0.23.0_py36
ml viz
ml py-scikit-learn/0.19.1_py36

python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/check_for_flag.py