#!/bin/bash -l

# EDIT THIS:
vuosi=2024
#. ./configCloudy.config
. confs/configCloudy2024.config

echo For Cloudy the project path is $projectpath


echo Generate command list for each cloudy data set...

#datasets=("1110" "1120" "1230" "1310" "1320" "1400" "2100" "2200" "3100" "4100" "4200" "1300")
datasets=("1110" "1120" "1230" "1310" "1320" "1400" "2100" "2200" "3100" "4100" "4200") # 1300 yhdistäminen tehdään vasta 07:ssa
bands=("B02" "B03" "B04" "B05" "B06" "B07" "B08" "B8A" "B11" "B12")

        #numero=$(echo $setti | sed 's/.*\([0-9]\{4\}\)/\1/')
        FILENAME=05-arrayjob-cloudy-histo-komento.txt
        #INPUT=/scratch/project_2009889/SISA/cloudy/results_2022-July
        INPUT=$projectpath
        OUTPUT=/scratch/project_2009889/cropyield2024/forecasting/cloudy/histo\_$vuosi

        if test -f $FILENAME; then
            rm $FILENAME
        fi

        touch $FILENAME

        echo For each band...
                for bandi in ${bands[@]}
                do
                        #. /scratch/project_2009889/cropyield_project1253/$bandi.config
                        . /projappl/project_2009889/cropyield_configs/$bandi.config
                        echo "python /projappl/project_2009889/cropyield2024/forecasting/python/05-histogramize-shadow.py -i $INPUT -o $OUTPUT -b $bandi -n 32 -l $minimi -u $maksimi" >> $FILENAME
                done



echo Running cloudy histo commands...
echo sbatch_commandlist -commands 05-arrayjob-cloudy-histo-komento.txt #  meni 40min July 15, default on 12h

