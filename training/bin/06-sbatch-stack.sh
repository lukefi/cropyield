#!/bin/bash -l
#SBATCH --job-name=2021-06-workflow
#SBATCH --output=jobs2021/output-06-histo2stack_out-%j.txt
#SBATCH --error=jobs2021/output-06-histo2stack_err.txt
#SBATCH --account=project_2009889
#SBATCH --time=01:00:00 # meni 20min
#SBATCH --mem=100G
#SBATCH --ntasks=1
#SBATCH --partition=small
#SBATCH --gres=nvme:100 #100G

#module load geoconda/3.8.8
module load geoconda

# EDIT:
vuosi=2021


#for vuosi in 2020 2020 2020 2021 2020; do

                echo histo_$vuosi
                tmpdir1=$LOCAL_SCRATCH/histo\_$vuosi\_temp1
                echo $tmpdir1
                #mkdir $tmpdir1

                #tmpdir2=$LOCAL_SCRATCH/histo\_$vuosi\_temp2
                #echo $tmpdir2
                #mkdir $tmpdir2

		echo python /projappl/project_2009889/cropyield2024/training/python/06-histo2stack.py -i /scratch/project_2009889/cropyield2024/training/cloudy/histo_$vuosi -n 32 -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack -f $vuosi.pkl -t $tmpdir1
		python /projappl/project_2009889/cropyield2024/training/python/06-histo2stack.py -i /scratch/project_2009889/cropyield2024/training/cloudy/histo_$vuosi -n 32 -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack -f $vuosi.pkl -t $tmpdir1

		#echo python /scratch/project_2009889/cropyield2024/training/python/06-histo2stack.py -i /scratch/project_2009889/cropyield2024/training/cloudless/histo_$vuosi -n 32 -o /scratch/project_2009889/cropyield2024/training/cloudless/dataStack -f $vuosi.pkl -t $tmpdir2
		#python /scratch/project_2009889/cropyield2024/training/python/06-histo2stack.py -i /scratch/project_2009889/cropyield2024/training/cloudless/histo_$vuosi -n 32 -o /scratch/project_2009889/cropyield2024/training/cloudless/dataStack -f $vuosi.pkl -t $tmpdir2

