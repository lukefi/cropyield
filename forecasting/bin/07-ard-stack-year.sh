#!/bin/bash -l

# Stack one year data from one crop type (setti)

#module load geoconda # must be > 3.9.
module load geoconda/3.10.9

#EDIT:
vuosi=2024

FILENAME=07-arrayjob-stackARDkomennot2024.txt

        if test -f $FILENAME; then
            rm $FILENAME
        fi

        touch $FILENAME

# MY 2020-09-15, 2021-02-22
# Make  stack files into one array stack.
# Now also year as input and can be multiple

#doPreworks=1; # set either 1 or 0
#if [ $doPreworks -eq 1 ]; then


datasets=("1110" "1120" "1230" "1310" "1320" "1400" "2100" "2200" "3100" "4100" "4200")

for setti in ${datasets[@]}
do

	#hakemistot=($(find histo_${setti}* -type d))
echo python /projappl/project_2009889/cropyield2024/forecasting/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack \
	-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack_annual -f ${setti} -y $vuosi >> $FILENAME


done

echo python /projappl/project_2009889/cropyield2024/forecasting/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack \
	-i /scratch/project_2009889/cropyield2024/forecasting/cloudy/dataStack_annual -f 1310 1320 -y $vuosi >> $FILENAME

#else
# make ARD with python:
	echo Aja: sbatch_commandlist -commands $FILENAME -t 00:20:00 -mem 100000 #  1min riittää

#sbatch_commandlist -commands $FILENAME

#fi



