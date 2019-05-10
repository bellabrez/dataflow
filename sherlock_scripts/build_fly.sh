#!/bin/bash
#SBATCH --job-name=build_fly
#SBATCH --partition=trc
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

ml python/3.6.1

echo "Bash - building fly."
python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/fly_builder.py
