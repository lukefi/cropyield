#!/bin/bash -l
#SBATCH --job-name=10-yields
#SBATCH --account=project_2009889
#SBATCH --output=jobs/output-10_out.txt
#SBATCH --error=jobs/output-10_err.txt
#SBATCH --time=00:04:00 
#SBATCH --mem=1G
#SBATCH --ntasks=1
#SBATCH --partition=test
##SBATCH --mail-type=END
##SBATCH --mail-user=maria.yli-heikkila@luke.fi

module load geoconda

cd /projappl/project_2009889/cropyield2024/forecasting/bin/


echo $(date)
TODAY=$(date +"%Y-%m-%d")

echo $TODAY


python ../python/10-calculateMeanYields.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/$TODAY

