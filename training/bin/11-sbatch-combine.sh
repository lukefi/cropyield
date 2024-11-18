#!/bin/bash
#SBATCH --job-name=11-combine
#SBATCH --account=project_2009889
#SBATCH --time=00:14:00
#SBATCH --ntasks=1
#SBATCH --partition=test

module load geoconda

python ../python/11-combineResults.py -i /scratch/project_2009889/cropyield2024/training/cloudy/predictions/2024-06-07

cat /scratch/project_2009889/cropyield2024/training/cloudy/predictions/2024-06-07/combinedResults.csv
