#!/bin/bash
#SBATCH --job-name=splitshp
#SBATCH --output=/projappl/project_2009889/cropyield2024/training/bin/jobs2023/output-01-splitshp_out-2023.txt
#SBATCH --error=output-01-splitshp_err.txt
#SBATCH --account=project_2009889
#SBATCH --time=00:14:00
#SBATCH --ntasks=1
#SBATCH --partition=test

module load geoconda

if test -f /scratch/project_2009889/cropyield2024/training/logs/intersections-2023.tsv; then
    rm /scratch/project_2009889/cropyield2024/training/logs/intersections-2023.tsv
fi

python /projappl/project_2009889/cropyield2024/training/python/01-splitshp-shadow.py --s2tiles /scratch/project_2009889/sentinel2_tiles_world/suomiTiles.shp \
 --fullshapefile  /scratch/project_2009889/cropyield2024/training/shpfiles/training-2023/satotilat-2023-all-2100.shp \
 --outshpdir /scratch/project_2009889/cropyield2024/training/shpfiles/shpfiles_perTile/viljat-2023 -o /scratch/project_2009889/cropyield2024/training/logs/intersections-2023.tsv

nrtiles=$(cat /scratch/project_2009889/cropyield2024/training/logs/intersections-2023.tsv| cut -f3 -d,| sort| uniq| wc -l)
tiles=$(cat /scratch/project_2009889/cropyield2024/training/logs/intersections-2023.tsv| cut -f3 -d,| sort| uniq -c)
echo "There are $nrtiles tiles:\n $tiles"

