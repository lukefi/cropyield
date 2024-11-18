#!/bin/bash -l

# Stack one year data from one crop type (setti)
# needed for a) forecasting, b) in training for leave-1-out evaluation.

module load geoconda # must be 3.9.

#EDIT:
vuosi=2021

FILENAME=jobs2021/07-arrayjob-stackARDkomennot2021.txt

        if test -f $FILENAME; then
            rm $FILENAME
        fi

        touch $FILENAME

# MY 2020-09-15, 2021-02-22
# Make  stack files into one array stack.
# Now also year as input and can be multiple

#doPreworks=1; # set either 1 or 0
#if [ $doPreworks -eq 1 ]; then


#datasets=("1110" "1120" "1230" "1310" "1320" "1400")
#datasets=("2100" "2200" "3100" "4100" "4200")
datasets=("1110" "1120" "1230" "1310" "1320" "1400" "2100" "2200" "3100" "4100" "4200")

for setti in ${datasets[@]}
do

	#hakemistot=($(find histo_${setti}* -type d))
 
		echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -f ${setti} -y $vuosi >> $FILENAME

		#echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudless/dataStack \
		#	-i /scratch/project_2009889/cropyield2024/training/cloudless/dataStack_annual -f ${setti} -y $vuosi >> $FILENAME
done

#else
# make ARD with python:
        echo Yhden vuoden ajoihin riittää default muisti ja pari minuuttia eli voisi ajaa testissä.
	echo Aja: sbatch_commandlist -commands 07-arrayjob-stackARDkomennot2021.txt -t 00:10:00 #  1min riittää

#sbatch_commandlist -commands $FILENAME

#fi



