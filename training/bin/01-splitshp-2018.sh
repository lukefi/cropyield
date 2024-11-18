#!/bin/bash
#SBATCH --job-name=splitshp
#SBATCH --output=/projappl/project_2009889/cropyield2024/training/bin/jobs2018/output-01-splitshp_out-2018.txt
#SBATCH --error=output-01-splitshp_err.txt
#SBATCH --account=project_2009889
#SBATCH --time=00:14:00
#SBATCH --ntasks=1
#SBATCH --partition=test

module load geoconda

if test -f /scratch/project_2009889/cropyield2024/training/logs/intersections-2018.tsv; then
    rm /scratch/project_2009889/cropyield2024/training/logs/intersections-2018.tsv
fi

python /projappl/project_2009889/cropyield2024/training/python/01-splitshp-shadow.py --s2tiles /scratch/project_2009889/sentinel2_tiles_world/suomiTiles.shp \
 --fullshapefile  /scratch/project_2009889/cropyield2024/training/shpfiles/training-2018/satotilat-2018-all.shp \
 --outshpdir /scratch/project_2009889/cropyield2024/training/shpfiles/shpfiles_perTile/viljat-2018 -o /scratch/project_2009889/cropyield2024/training/logs/intersections-2018.tsv

nrtiles=$(cat /scratch/project_2009889/cropyield2024/training/logs/intersections-2018.tsv| cut -f3 -d,| sort| uniq| wc -l)
tiles=$(cat /scratch/project_2009889/cropyield2024/training/logs/intersections-2018.tsv| cut -f3 -d,| sort| uniq -c)
echo "There are $nrtiles tiles:\n $tiles"

