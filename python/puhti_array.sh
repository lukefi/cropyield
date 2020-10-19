#!/bin/bash -l
#SBATCH --job-name=array_job
#SBATCH --output=array_job_out_%A_%a.txt
#SBATCH --error=array_job_err_%A_%a.txt
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=12000


module load geoconda

. ./config.config

name=$(sed -n ${SLURM_ARRAY_TASK_ID}p bandpaths.txt)

python arrayextractor.py -f $name -shp $shppath -p $projectpath -jn ${SLURM_ARRAY_TASK_ID} -id $idname

rm -rf $projectpath/${SLURM_ARRAY_TASK_ID}



