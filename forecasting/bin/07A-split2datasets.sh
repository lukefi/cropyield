#!/bin/bash -l
#SBATCH --job-name=07A
#SBATCH --output=jobs/output-07A-split_out-%j.txt
#SBATCH --error=jobs/output-07A-split_err.txt
#SBATCH --account=project_2009889
#SBATCH --time=01:40:00 # meni 
#SBATCH --mem=230G # 130G riitti heinäkuun loppuun asti
#SBATCH --ntasks=1
#SBATCH --partition=small

#module load geoconda
#module load geoconda/3.8.8
module load geoconda/3.10.9

#EDIT:
vuosi=2024

python /projappl/project_2009889/cropyield2024/forecasting/python/07A-split2separateSets.py \
			-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack_annual -y $vuosi
# UT 2024-06-18
# Run the preparation step for 07 here
/projappl/project_2009889/cropyield2024/forecasting/bin/07-ard-stack-year.sh
