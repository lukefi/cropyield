#!/bin/bash -l

# Stack years of crop wise data sets for a) training the final model with all years, b) for leave-1-out evaluation in training.

echo Remember: module load geoconda


FILENAME=07-arrayjob-stackARDkomennot-years-to-training-set.txt

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
datasets=("1110" "1120" "1230" "1310" "1320" "1400" "2100" "2200" "3100" "4100" "4200")

for setti in ${datasets[@]}
do

	#hakemistot=($(find histo_${setti}* -type d))
 
		echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -f ${setti} -y 2018 2019 2020 2021 2022 2023 >> $FILENAME

		echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -f ${setti} -y 2018 2019 2020 2021 2022  >> $FILENAME

		echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -f ${setti} -y 2018 2019 2020 2021 2023  >> $FILENAME

		echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -f ${setti} -y 2018 2019 2020 2022 2023 >> $FILENAME

		echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -f ${setti} -y 2018 2019 2021 2022 2023 >> $FILENAME

		echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -f ${setti} -y 2018 2020 2021 2022 2023 >> $FILENAME

		echo python /projappl/project_2009889/cropyield2024/training/python/07-stack2ARD.py -o /scratch/project_2009889/cropyield2024/training/cloudy/dataStack \
			-i /scratch/project_2009889/cropyield2024/training/cloudy/dataStack_annual -f ${setti} -y 2019 2020 2021 2022 2023 >> $FILENAME

done

#else
# make ARD with python:
#	echo Aja: sbatch_commandlist -commands stackARDkomennot.txt -t 00:10:00 -mem 20000 #  1min riittää

echo Aja: sbatch_commandlist -commands $FILENAME -t 00:10:00 -mem 200G # vaatii paljon muistia


#fi



