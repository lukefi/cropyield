# cropyield2024
Operational crop yield forecasting system for summer 2024


## Forecasting:

### Preparation:
- 00 from parcel geometries, prepare Shapefile (local computer)
- 01 split Shapefile by S2 tiles (some tiles have hundreds of parcels, some tiles have less than 10) (Puhti test partition)


### Repeated steps:
- 02 select S2 filepaths by time filter (start, end) (test partition)
- 03 extract parcel wise values from S2 images (array job, 25,000 commands)
- 05 from vector values into historgrams (array job, 10 commands)
- 06 stack data from files into pandas dataframe (sbatch)
- 07A split data by crop type in to separate files (sbatch)
- 07 reshape data from dataframe into numpy array of shape (observations, time, features). (for each crop separately, array job of 6 or 11 commands)
- 09 use model M to predict parcel-wise yields (sbatch GPU)
- 10 calculate regional yields (area-weighted means) and save into long term s3 data storage (sbatch)
- 20 make maps of yield forecasts for each crops and save into long term s3 data storage (sbatch)
- 30 send email with links to new products in s3 data storage (sbatch)

## Training:

- 00 from parcel geometries, prepare Shapefile (local computer)
- 01 split Shapefile by S2 tiles (some tiles have hundreds of parcels, some tiles have less than 10) (Puhti test partition)
- 02 select S2 filepaths by time filter (start, end) (test partition)
- 03 extract parcel wise values from S2 images (array job, 25,000 commands)
- 05 from vector values into historgrams (array job, 10 commands)
- 06 stack data from files into pandas dataframe (sbatch)
- 07A split data by crop type in to separate files (sbatch)
- 07 run for one year (testing) and also combine multiple years (training) for reshaping data from dataframe into numpy array of shape (observations, time, features). (for each crop separately, array job of 6 or 11 commands)
- 09 run TCN (leave-1-out) for reporting error for each excluded year (for studying how the model works) (sbatch GPU)
- ... evaluate modelling results in MLFlow interface ...
- 09 with the best performing hyperparameter set train the model (all years used for training the final model) (sbatch GPU)
- 11 optionally, for reporting RMSE (sbatch)
- 17 draw some plots of predictions vs. true yields (sbatch)



## Funding acknowledgements

This work was supported by the European Union (Grant Agreement 101037619-2020-FI-AGRI – Work Package 2).

![Funded by Eurostat](img/Eurostat_logo_RGB_200-small.png)



