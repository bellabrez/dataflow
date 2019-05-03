#!/bin/bash
#SBATCH --job-name=test
#SBATCH --partition=trc
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

ml python/3.6.1

python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/fly_builder.py