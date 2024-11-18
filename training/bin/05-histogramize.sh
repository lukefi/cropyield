#!/bin/bash -l

# EDIT THIS:
vuosi=2021
#. ./configCloudy.config
. confs/configCloudy2021.config

echo For Cloudy the project path is $projectpath


echo Generate command list for each cloudy data set...

bands=("B02" "B03" "B04" "B05" "B06" "B07" "B08" "B8A" "B11" "B12")

        #numero=$(echo $setti | sed 's/.*\([0-9]\{4\}\)/\1/')
        FILENAME=jobs2021/05-arrayjob-cloudy-histo-komento.txt
        #INPUT=/scratch/project_2009889/SISA/cloudy/results_2021-July
        INPUT=$projectpath
        OUTPUT=/scratch/project_2009889/cropyield2024/training/cloudy/histo\_$vuosi

        if test -f $FILENAME; then
            rm $FILENAME
        fi

        touch $FILENAME

        echo For each band...
                for bandi in ${bands[@]}
                do
                        . /projappl/project_2009889/cropyield_configs/$bandi.config
                        echo "python /projappl/project_2009889/cropyield2024/training/python/05-histogramize-shadow.py -i $INPUT -o $OUTPUT -b $bandi -n 32 -l $minimi -u $maksimi" >> $FILENAME
                done



echo Running cloudy histo commands...
echo sbatch_commandlist -commands 05-arrayjob-cloudy-histo-komento.txt
