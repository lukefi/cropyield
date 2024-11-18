#!/bin/bash -l
#SBATCH --job-name=sentinel-download
#SBATCH --account=project_2009889
#SBATCH --time=01:00:00 
#SBATCH --mem=2G
#SBATCH --ntasks=1
#SBATCH --partition=small

export PATH="$PATH:/projappl/project_2009889/cropyield2024/forecasting/bin"

# Terminate looping on  1.9.2024
STOPDATE=$(date +%s -d 2024-09-01)
CURDATE=$(date +%s)

if [[ $CURDATE -gt $STOPDATE ]]; then
        exit
fi

module load allas

00-Sentinel.sh

sbatch -b tomorrow sentinel-download.sh

