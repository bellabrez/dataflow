#!/bin/bash
#SBATCH --job-name=bldmnbrn
#SBATCH --partition=trc
#SBATCH --time=1-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --open-mode=append
#SBATCH --output=./logs/mainlog.out

ml python/3.6.1
date
python3 -u /home/users/brezovec/projects/dataflow/sherlock_scripts/20220627_meanbrain_creation_subvol.py