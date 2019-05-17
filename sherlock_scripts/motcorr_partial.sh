#!/bin/bash
#SBATCH --job-name=motcorr_partial
#SBATCH --partition=trc
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

some_var="$1"
echo "$some_var"