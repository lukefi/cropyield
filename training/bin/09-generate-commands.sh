#!/bin/bash -l

module load geoconda # must be 3.9.

#EDIT:

FILENAME=runTCN-leaveOneOut-commands2023.txt

        if test -f $FILENAME; then
            rm $FILENAME
        fi

        touch $FILENAME

datasets=("1110" "1120" "1230" "1310" "1320" "1400" "2100" "2200" "3100" "4100" "4200")
years=("2018" "2019" "2020" "2021" "2022" "2023")

for setti in ${datasets[@]}
do
for year in ${years[@]}
do

 
		#echo python /scratch/project_2009889/cropyield2023/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2023/training/cloudy/dataStack \
		#	-i /scratch/project_2009889/cropyield2023/training/cloudy/dataStack_annual -f ${setti} -y $vuosi >> $FILENAME

		#echo python /scratch/project_2009889/cropyield2023/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2023/training/cloudless/dataStack \
		#	-i /scratch/project_2009889/cropyield2023/training/cloudless/dataStack_annual -f ${setti} -y $vuosi >> $FILENAME

echo python /projappl/project_2009889/cropyield2023/training/python/09-runTCN-leaveOneOut.py \
-i /scratch/project_2009889/cropyield2023/training/cloudy/dataStack_ard/array_$setti-2018-2019-2020-2021-2022-2023.npz \
-j /scratch/project_2009889/cropyield2023/training/cloudy/dataStack_ard/array_$setti-$year.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -n leaveoneout -d Year $year is left out >> $FILENAME

# täytyy sitten käsin editoida  pois testing vuosi training filenimestä

done
done
