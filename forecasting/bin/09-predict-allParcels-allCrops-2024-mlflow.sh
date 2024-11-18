#!/bin/bash
#SBATCH --job-name=09-predict-TCN-mlflow
#SBATCH --output=jobsPredict/output-09_TCN_predict-new-year_out-%j.txt
#SBATCH --error=jobsPredict/output-09_TCN_predict-new-year_err.txt
#SBATCH --partition=gpu
# SBATCH --partition=gputest
#SBATCH --nodes=1
#SBATCH --gres=gpu:v100:1
#SBATCH --time=03:30:00 # 1h16min meni end of June, 1h53min mid-July, 3h ei riittänyt end of August
# SBATCH --time=00:10:00
#SBATCH --mem-per-cpu=200G # oli 100G
#SBATCH --cpus-per-task=1
#SBATCH --account=project_2009889

module load tensorflow
# module load allas
# allas-conf --mode s3 -u rb_2009889_allas01
# 18.7. laitoin uudestaan, kun oli häikkää

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_1110-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_1120-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_1230-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_1310-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_1320-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_1400-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_1310-1320-2024.npz # 1300: 123360 lohkoa, 18min

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_2100-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_2200-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_3100-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_4100-2024.npz

srun python /projappl/project_2009889/cropyield2024/forecasting/python/09-predict-mlflow.py \
-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack/array_4200-2024.npz




