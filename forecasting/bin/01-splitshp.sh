#!/bin/bash
#SBATCH --job-name=01-splitshp
#SBATCH --output=jobs/output-01-splitshp_out-2024.txt
#SBATCH --error=jobs/output-01-splitshp_err.txt
#SBATCH --account=project_2009889
#SBATCH --time=00:14:00
#SBATCH --ntasks=1
#SBATCH --partition=small

module load geoconda

echo "I have done 01 already once this year. No need to repeat it. I will take a nap."
sleep 5

# Do below when running the first time:
#python /projappl/project_2009889/cropyield2024/forecasting/python/01-splitshp-shadow.py --s2tiles /scratch/project_2009889/sentinel2_tiles_world/suomiTiles.shp \
# --fullshapefile  /scratch/project_2009889/cropyield2024/forecasting/shpfiles/forecasting-2024/parcels-2024.shp \
# --outshpdir /scratch/project_2009889/cropyield2024/forecasting/shpfiles/shpfiles_perTile/viljat-2024 -o /scratch/project_2009889/cropyield2024/forecasting/logs/intersections-2024.tsv

#nrtiles=$(cat /scratch/project_2009889/cropyield2024/forecasting/logs/intersections-2024.tsv| cut -f3 -d,| sort| uniq| wc -l)
#tiles=$(cat /scratch/project_2009889/cropyield2024/forecasting/logs/intersections-2024.tsv| cut -f3 -d,| sort| uniq -c)
#echo "There are $nrtiles tiles:\n $tiles"

# UT 2024-06-18
# Restart workflow for the next day
#/projappl/project_2009889/cropyield2024/forecasting/bin/full_workflow
