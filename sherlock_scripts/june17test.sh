#!/bin/bash
#SBATCH --job-name=main_launch
#SBATCH --partition=trc
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=./logs/mainlog.out
#SBATCH --open-mode=append

ml python/3.6.1
date
python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/june17test.py