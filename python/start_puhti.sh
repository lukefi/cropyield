. ./config.config

python pathfinder.py -s $startdate -e $enddate  -d $datapath

count=$(wc -l < bandpaths.txt)

##run EODIE array job
echo "starting Puhti Array job"

sbatch --array=1-$count --account=$puhtiproject puhti_array.sh 


