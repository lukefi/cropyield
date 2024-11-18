module load geoconda

echo Generate command list for set Cloudy

# EDIT:
#. ./configCloudy.config
. confs/configCloudy2024.config

echo Shape path is $shppath
echo For Cloudy the project path is $projectpath


echo Choosing tiles...

# Each data set (shp) are spread on different set of tiles. We choose only relevant tiles.

#ls -1 $shppath | cut -f4 -d\_ | cut -f1 -d\. | sort | uniq > tiles.txt

grep -f confs/37-tiles.txt bandpaths.txt > bandpaths2.txt

rivi_lkm=$(cat bandpaths2.txt | wc -l)

echo Write commands to a file...

if test -f 03-arrayjob-komennotCloudy.txt; then
    rm 03-arrayjob-komennotCloudy.txt
fi

touch 03-arrayjob-komennotCloudy.txt

for ID in $( seq 1 $rivi_lkm)
do
   name=$(sed -n ${ID}p bandpaths2.txt)
   echo "python /projappl/project_2009889/cropyield2024/forecasting/python/03-arrayextractor.py -f $name -shp $shppath -p $projectpath -jn ${ID} -id $idname -r 10 -t \$LOCAL_SCRATCH" >> 03-arrayjob-komennotCloudy.txt
done




    if [[ ! -d $projectpath ]]
    then
        echo "Creating directory ${projectpath}"
        mkdir -p $projectpath
    fi

echo Muista module load geoconda #/3.8.8!
#echo Run sbatch_commandlist -commands komennotCloudless.txt -t 16:40:00 -mem 9000 --tmp 2000
echo Run sbatch_commandlist -commands 03-arrayjob-komennotCloudy.txt -t 16:40:00 -mem 9000 --tmp 2000

echo sbatch_commandlist -commands 03-arrayjob-komennotCloudy.txt -t 02:00:00 -mem 9000 --tmp 2000 # pitäis riittää
