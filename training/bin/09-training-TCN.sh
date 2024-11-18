#!/bin/bash
#SBATCH --job-name=TCN
#SBATCH --output=TCN_out-%j.txt
#SBATCH --error=TCN_err-%j.txt
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gres=gpu:v100:1
#SBATCH --time=3:00:00 # meni 2:18h
#SBATCH --mem=64G
#SBATCH --cpus-per-task=1
#SBATCH --account=project_2009889

# here comes training of predictions models for each crop type:

module load tensorflow

echo /projappl/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1110-2018-2019-2020-2021-2022.npz 
python /projappl/project_2009889/cropyield2024/training/python/09-runTCN.py -i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1110-2018-2019-2020-2021-2022.npz  \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -t

echo /projappl/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1120-2018-2019-2020-2021-2022.npz 
python /projappl/project_2009889/cropyield2024/training/python/09-runTCN.py -i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1120-2018-2019-2020-2021-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -t

echo /projappl/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1230-2018-2019-2020-2021-2022.npz 
python /projappl/project_2009889/cropyield2024/training/python/09-runTCN.py -i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1230-2018-2019-2020-2021-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -t

echo /projappl/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1310-2018-2019-2020-2021-2022.npz
python /projappl/project_2009889/cropyield2024/training/python/09-runTCN.py -i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1310-2018-2019-2020-2021-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -t

echo /projappl/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1320-2018-2019-2020-2021-2022.npz 
python /projappl/project_2009889/cropyield2024/training/python/09-runTCN.py -i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1320-2018-2019-2020-2021-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -t

echo /projappl/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1400-2018-2019-2020-2021-2022.npz 
python /projappl/project_2009889/cropyield2024/training/python/09-runTCN.py -i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_ard/array_1400-2018-2019-2020-2021-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -t

