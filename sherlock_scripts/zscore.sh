#!/bin/bash

directory="$1"
echo "$directory"
# POSITIONAL=()
# while [[ $# -gt 0 ]]
# do
# key="$1"

# case $key in
#     -d|--datadir)
#     DATADIR="$2"
#     shift # past argument
#     shift # past value
#     ;;
#     -c|--channels)
#     CHANNELS="$2"
#     shift # past argument
#     shift # past value
#     ;;
#     -l|--lib)
#     LIBPATH="$2"
#     shift # past argument
#     shift # past value
#     ;;
#     --default)
#     DEFAULT=YES
#     shift # past argument
#     ;;
#     *)    # unknown option
#     POSITIONAL+=("$1") # save it in an array for later
#     shift # past argument
#     ;;
# esac
# done
# set -- "${POSITIONAL[@]}" # restore positional parameters

# echo DATADIR         = "${DATADIR}"
# echo CHANNELS        = "${CHANNELS}"
# echo LIBRARY PATH    = "${LIBPATH}"
# echo DEFAULT         = "${DEFAULT}"

#ml gcc/6.3.0
#ml python/3.6.1
#ml py-numpy/1.14.3_py36
#ml py-pandas/0.23.0_py36
#ml viz
#ml py-scikit-learn/0.19.1_py36

#directory="$1"
#python3 /home/users/brezovec/projects/dataflow/sherlock_scripts/zscore.py "$directory"

#SBATCH --job-name=zscore
#SBATCH --partition=trc
#SBATCH --time=0:02:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=slurm_moco.out
#SBATCH --open-mode=truncate
