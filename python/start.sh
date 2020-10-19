. ./config.config

python pathfinder.py -s $startdate -e $enddate  -d $datapath

for name in $(cat bandpaths.txt)
do
    python arrayextractor.py -f $name -shp $shppath -p $projectpath -id $idname
done