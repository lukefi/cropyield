. ../example/config.config
echo $startdate

python ../python/pathfinder.py -s $startdate -e $enddate  -d $datapath -b 4

for name in $(cat bandpaths.txt)
do
    python ../python/arrayextractor.py -f $name -shp $shppath -p $projectpath -id $idname 
done