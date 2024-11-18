#!/bin/bash
#SBATCH --output=jobsTraining/output-08-make_out-%j.txt
#SBATCH --error=jobsTraining/output-08-make_err-%j.txt
#SBATCH --job-name=08-all
#SBATCH --account=project_2009889
#SBATCH --ntasks=1
# SBATCH --partition=test # yhdelle vuodelle riittää test
#SBATCH --partition=small
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=20G # Memory Utilized: 246.88 MB yhdelle vuodelle
#SBATCH --cpus-per-task=1

module load geoconda

# for one year only:
#python /projappl/project_2009889/cropyield2024/training/python/08-makeTarget.py -i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack/ -y 2021

# for all array files:
python /projappl/project_2009889/cropyield2024/training/python/08-makeTarget.py -i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack/
