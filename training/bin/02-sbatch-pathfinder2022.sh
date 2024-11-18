#!/bin/bash
#SBATCH --job-name=pathfinder
#SBATCH --account=project_2009889
#SBATCH --time=00:14:00
#SBATCH --ntasks=1
#SBATCH --partition=test

module load geoconda

. confs/configCloudy2022.config

echo SAFE dirs are in $datapath

python /projappl/project_2009889/cropyield2024/training/python/02-pathfinder.py -s 20220501 -e 20220901  -d $datapath

cp bandpaths.txt bandpaths.txt2022
