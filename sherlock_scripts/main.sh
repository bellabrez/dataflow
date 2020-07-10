#!/bin/bash
#SBATCH --job-name=dataflow
#SBATCH --partition=trc
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=./logs/mainlog.out
#SBATCH --open-mode=append
#SBATCH --mail-type=ALL

ml python/3.6.1
date
python3 -u /home/users/brezovec/projects/dataflow/sherlock_scripts/main.py
#python3 -u /home/users/brezovec/projects/dataflow/sherlock_scripts/temp_moco_test.py