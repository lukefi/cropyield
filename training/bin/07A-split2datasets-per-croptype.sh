#!/bin/bash -l
#SBATCH --job-name=2021-07A
#SBATCH --output=jobs2021/output-07A-split_out.txt
#SBATCH --error=output-07A-split_err.txt
#SBATCH --account=project_2009889
# SBATCH --time=00:30:00 # tai 2h
#SBATCH --mem=100G
#SBATCH --ntasks=1
#SBATCH --partition=test

module load geoconda

#EDIT:
vuosi=2021

#for vuosi in 2020 2020 2020 2021 2020; do




python /projappl/project_2009889/cropyield2024/training/python/07A-split2separateSets.py \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -y $vuosi


#done
