#!/bin/bash
#SBATCH --job-name=02-pathfinder
#SBATCH --account=project_2009889
#SBATCH --time=00:54:00
#SBATCH --ntasks=1
#SBATCH --partition=small

#module load geoconda
module load geoconda/3.10.9

. confs/configCloudy2024.config

echo SAFE dirs are in $datapath

python /projappl/project_2009889/cropyield2024/forecasting/python/02-pathfinder.py -s $startdate -e $enddate  -d $datapath

cp bandpaths.txt bandpaths.txt$(date +"%Y%m%d")

# UT 2024-06-18
# Prepre for the next steps here
/projappl/project_2009889/cropyield2024/forecasting/bin/03-arrayextractor.sh

export PATH="$PATH:/projappl/project_2009889/cropyield2024/forecasting/bin"


# UT 2024-07-17
# Remove environment variables that messes up further jobs
export -n SLURM_MEM_PER_CPU
export -n SLURM_MEM_PER_GPU
export -n SLURM_MEM_PER_NODE


# Terminate looping on  1.9.2024
STOPDATE=$(date +%s -d 2024-09-01)
CURDATE=$(date +%s)

if [[ ! $CURDATE -gt $STOPDATE ]]; then
       # UT 2024-06-18 
       # Restart workflow for the next day 
       /projappl/project_2009889/cropyield2024/forecasting/bin/full_workflow 
fi



job4=$(sbatch_commandlist-silent -commands 03-arrayjob-komennotCloudy.txt -t 02:00:00 -mem 9000 --tmp 80) # meni max 1h40min ja temp 17GB


# MY added 2024-07-29: if it is Monday
#if [[ $(date +%u) -eq 1 ]]; then 

#job5=$(sbatch_w --dependency=afterok:$job4 05-histogramize-2024.sh)
job5=$(sbatch_commandlist-silent -dependency afterok:$job4 -commands 05-arrayjob-cloudy-histo-komento.txt) # meni max 31min
job6=$(sbatch_w --dependency=afterok:$job5 06-sbatch-stack.sh) # meni 35min
job7=$(sbatch_w --dependency=afterok:$job6 07A-split2datasets.sh) # meni 8 min
job8=$(sbatch_commandlist-silent -dependency afterok:$job7 -commands 07-arrayjob-stackARDkomennot2024.txt -mem 150000) # mem was 100000, in the end of August needed more memory
job9=$(sbatch_w --dependency=afterok:$job8 09-predict-allParcels-allCrops-2024-mlflow.sh)
job10=$(sbatch_w --dependency=afterok:$job9 10-calculateYields.sh)
job11=$(sbatch_w --dependency=afterok:$job10 20-runMakingMaps.sh)
job12=$(sbatch_w --dependency=afterok:$job11 30-sendEmail.sh)

	echo Launched 03 as jobid $job4, 05 as $job5, 06 as $job6, 07A as $job7, 07 as $job8, 09 as jobid $job9, mean yields as jobid $job10, maps as jobid $job11, and emailing jobid $job12
#fi

