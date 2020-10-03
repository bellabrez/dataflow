#!/bin/bash
#SBATCH --job-name=loop
#SBATCH --partition=trc
#SBATCH --time=3-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=./logs/mainlog.out
#SBATCH --open-mode=append

ml python/3.6.1
date
python3 -u /home/users/brezovec/projects/dataflow/sherlock_scripts/loop.py
#python3 -u /home/users/brezovec/projects/dataflow/sherlock_scripts/temp_moco_test.py
#SBACTH --nodelist=sh02-07n34
#SBATCH --mail-type=ALL
