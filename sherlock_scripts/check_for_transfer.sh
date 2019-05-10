#!/bin/bash
#SBATCH --job-name=check_transfer
#SBATCH --partition=trc
#SBATCH --time=0:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

ml python/3.6.1

#chmod +x build_fly.sh

echo "Bash - Checking for flag"

python3 chmod +x /home/users/brezovec/projects/dataflow/sherlock_scripts/check_for_flag.py