#!/bin/bash -l
#SBATCH --job-name=06-stack
#SBATCH --output=jobs/output-06-histo2stack_out-%j.txt
#SBATCH --error=jobs/output-06-histo2stack_err.txt
#SBATCH --account=project_2009889
#SBATCH --time=02:00:00 # meni 26min mid-July, 1h riitti melkein elokuun loppuun
#SBATCH --mem=200G # 130G loppui heinäkuun lopussa
#SBATCH --ntasks=1
#SBATCH --partition=small
#SBATCH --gres=nvme:100 #100G

#module load geoconda/3.8.8
module load geoconda/3.10.9

# EDIT:
vuosi=2024


# MY 2020-09-15, 2021-02-22, 2021-08-30, 2021-11-21, 2022-03-20

	#hakemistot=($(find histo_${setti}* -type d))

		echo histo_$vuosi
                tmpdir1=$LOCAL_SCRATCH/histo\_$vuosi\_temp1
                echo $tmpdir1
                #mkdir $tmpdir1

		echo python /projappl/project_2009889/cropyield2024/forecasting/python/06-histo2stack.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/histo_$vuosi -n 32 -o /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack -f $vuosi.pkl -t $tmpdir1
		python /projappl/project_2009889/cropyield2024/forecasting/python/06-histo2stack.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/histo_$vuosi -n 32 -o /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack -f $vuosi.pkl -t $tmpdir1


