#!/bin/bash
#SBATCH --job-name=pathfinder
#SBATCH --account=project_2009889
#SBATCH --time=00:14:00
#SBATCH --ntasks=1
#SBATCH --partition=test

module load geoconda

. confs/configCloudy2023.config

echo SAFE dirs are in $datapath

python /projappl/project_2009889/cropyield2024/training/python/02-pathfinder.py -s 20230501 -e 20230901  -d $datapath

cp bandpaths.txt bandpaths.txt2023
