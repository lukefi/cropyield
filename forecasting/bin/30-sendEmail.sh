#!/bin/bash -l
#SBATCH --job-name=30-email
#SBATCH --account=project_2009889
#SBATCH --output=jobs/output-30_out.txt
#SBATCH --error=jobs/output-30_err.txt
#SBATCH --time=00:14:00 
#SBATCH --mem=1G
#SBATCH --ntasks=1
#SBATCH --partition=small
##SBATCH --mail-type=END
##SBATCH --mail-user=maria.yli-heikkila@luke.fi

module load geoconda/3.10.9

cd /projappl/project_2009889/cropyield2024/forecasting/bin/

##### CLEAN UP:

# Remove array job task files as obsolete:
rm array_job_*_tmp.sh

# Remove empty array job files:
#for file in array_job_out_*.txt;
#do
#		if [ ! -s $file ]; then rm $file; 
#		fi
#done

#for file in array_job_err_*.txt;
#do
#		if [ ! -s $file ]; then rm $file; 
#		fi
#done

find -name "array_job_out_*.txt" -size 0 -delete 
find -name "array_job_err_*.txt" -size 0 -delete 

# Write the rest of the array job outputs into one file:
cat array_job_out_*.txt > jobs/output-07.txt-$(date +"%Y-%m-%d")
# Remove the rest of the array job outputs:
rm array_job_out_*.txt

##### END OF CLEAN UP


echo "Koko maan painotetut ennusteet $(date +"%d.%m.%Y"): " > email_contents

cat /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/$(date +"%Y-%m-%d")/keskisadot.csv >> email_contents

#echo "$(date +"%d.%m.%Y") päivitetyt satoennusteet:" > email_contents
#echo $(date) >> email_contents


echo -e "\n\nKuvat satoennusteista tiedostoissa: " >> email_contents

echo "
Kevätvehnä 1120:
https://a3s.fi/satoennusteet2024/Satoennuste-1120.png
https://a3s.fi/satoennusteet2024/Satoennuste-1120-10kmruutu-yield.png

Rehuohra 1310:
https://a3s.fi/satoennusteet2024/Satoennuste-1310.png
https://a3s.fi/satoennusteet2024/Satoennuste-1310-10kmruutu-yield.png

Mallasohra 1320:
https://a3s.fi/satoennusteet2024/Satoennuste-1320.png
https://a3s.fi/satoennusteet2024/Satoennuste-1320-10kmruutu-yield.png

Kaura 1400:
https://a3s.fi/satoennusteet2024/Satoennuste-1400.png
https://a3s.fi/satoennusteet2024/Satoennuste-1400-10kmruutu-yield.png" >> email_contents

echo -e "\n\nAikasarjat maakunnittain tiedostoissa: " >> email_contents

echo "
Syysvehnä 1110:
https://a3s.fi/satoennusteet2024/1110-maakunnittain.csv 

Kevätvehvä 1120:
https://a3s.fi/satoennusteet2024/1120-maakunnittain.csv

Ruis 1230:
https://a3s.fi/satoennusteet2024/1230-maakunnittain.csv

Rehuohra 1310:
https://a3s.fi/satoennusteet2024/1310-maakunnittain.csv

Mallasohra 1320:
https://a3s.fi/satoennusteet2024/1320-maakunnittain.csv

Ohra 1300:
https://a3s.fi/satoennusteet2024/1300-maakunnittain.csv

Kaura 1400:
https://a3s.fi/satoennusteet2024/1400-maakunnittain.csv

Herne 2100:
https://a3s.fi/satoennusteet2024/2100-maakunnittain.csv

Härkäpapu 2200:
https://a3s.fi/satoennusteet2024/2200-maakunnittain.csv

Peruna 3100:
https://a3s.fi/satoennusteet2024/3100-maakunnittain.csv

Rypsi 4100:
https://a3s.fi/satoennusteet2024/4100-maakunnittain.csv

Rapsi 4200:
https://a3s.fi/satoennusteet2024/4200-maakunnittain.csv" >> email_contents


# This reads the file "email_contents" and sends it as email
python3 ../python/30-sendmail.py -s maria.yli-heikkila@luke.fi
#python3 ../python/30-sendmail.py -s anneli.partala@luke.fi

#if [[ $(date +%u) -gt 1]]; then # if it is not Monday
if [[ $(date +%u) -eq 1 ]]; then # if it is Monday

python3 ../python/30-sendmail.py -s anneli.partala@luke.fi
#python3 ../python/30-sendmail.py -s terhi.taulavuori@luke.fi

fi
