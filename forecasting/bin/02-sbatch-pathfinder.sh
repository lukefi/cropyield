#!/bin/bash
#SBATCH --job-name=02-pathfinder
#SBATCH --account=project_2009889
#SBATCH --output=jobs/output-02_out.txt
#SBATCH --error=jobs/output-02_err.txt
#SBATCH --time=00:24:00
#SBATCH --ntasks=1
#SBATCH --partition=small

module load geoconda

. confs/configCloudy2024.config

echo SAFE dirs are in $datapath

python /projappl/project_2009889/cropyield2024/forecasting/python/02-pathfinder.py -s $startdate -e $enddate  -d $datapath

cp bandpaths.txt bandpaths.txt2024

# UT 2024-06-18
# Prepre for the next steps here
/projappl/project_2009889/cropyield2024/forecasting/bin/03-arrayextractor.sh

export PATH="$PATH:/projappl/project_2009889/cropyield2024/forecasting/bin"

# UT 2024-06-18 
# Restart workflow for the next day 
/projappl/project_2009889/cropyield2024/forecasting/bin/full_workflow2

