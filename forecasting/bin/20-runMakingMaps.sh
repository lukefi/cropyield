#!/bin/bash -l
#SBATCH --job-name=20-maps
#SBATCH --account=project_2009889
#SBATCH --output=jobs/output-20_out.txt
#SBATCH --error=jobs/output-20_err.txt
#SBATCH --time=00:44:00 
#SBATCH --mem=1G
#SBATCH --ntasks=1
#SBATCH --partition=small
##SBATCH --mail-type=END
##SBATCH --mail-user=maria.yli-heikkila@luke.fi

module load geoconda/3.10.9

echo $(date)
TODAY=$(date +"%Y-%m-%d")

echo $TODAY

# in Mac:
#python ../python/20-makeMaps-withRegional-predictions.py -v 2021 -c 1120 -d 2023-08-25 -o /Users/myliheik/Documents/mySISA/img
#python ../python/20-makeMaps-withRegional-predictions.py -v 2021 -c 1110 -d 2023-08-25 -o /Users/myliheik/Documents/mySISA/img
#python ../python/20-makeMaps-withRegional-predictions.py -v 2021 -c 1230 -d 2023-08-25 -o /Users/myliheik/Documents/mySISA/img
#python ../python/20-makeMaps-withRegional-predictions.py -v 2021 -c 1310 -d 2023-08-25 -o /Users/myliheik/Documents/mySISA/img
#python ../python/20-makeMaps-withRegional-predictions.py -v 2021 -c 1320 -d 2023-08-25 -o /Users/myliheik/Documents/mySISA/img
#python ../python/20-makeMaps-withRegional-predictions.py -v 2021 -c 1400 -d 2023-08-25 -o /Users/myliheik/Documents/mySISA/img


#python 20-yield-grid-maps.py -c 1310 \
#-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/2024-06-20/ \
#-o /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/2024-06-20/img/ \
#-y 2023 2024

python ../python/20-make-maps-Finnish-yield.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/$TODAY/
python ../python/20-make-maps-Finnish-yield.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/$TODAY/ -r gridded

python ../python/20-make-maps-Finnish-deviation.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/$TODAY/
python ../python/20-make-maps-Finnish-deviation.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/$TODAY/  -r gridded

python ../python/20-make-maps-yield.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/$TODAY/ -r gridded
python ../python/20-make-maps-deviation.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/$TODAY/

