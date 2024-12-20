#!/bin/bash

file=confs/37-tiles.txt

###############
# Script to 
# 1. Query Copernicus Data Space Ecosystem Sentinel-2 catalog based on startdate, enddate, cloudcover and tilename 
# 2. Download the found data from CDSE object storage to Allas object storage
#
# Requirements: Rclone setup to work with allas as [s3allas] (s3 setup connected to CSC project for Allas) and CDSE as [cdse] 
#
# Do: allas-conf --mode s3
# Written by Samantha Wittke, CSC - IT center for Science, based on script provided by Maria Yli-Heikkilä

TILES=("T34VDM" "T34VEM" "T34VEN" "T34VEP" "T34VEQ" "T34VER" "T34VFM" "T34VFN" "T34VFP" "T34VFQ" "T34VFR" "T34WFS" "T34WFT" "T34WFU" "T35VLG" "T35VLH" "T35VLJ" "T35VLK" "T35VLL" "T35VMG" "T35VMH" "T35VMJ" "T35VMK" "T35VML" "T35VNH" "T35VNJ" "T35VNK" "T35VNL" "T35VPJ" "T35VPK" "T35VPL" "T35WMM" "T35WMN" "T35WNM" "T36VUP" "T36VUQ" "T36VUR") 
BASEURL="http://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?"
BUCKETBASENAME="Sentinel2-MSIL2A-cloud-0-95"

LASTDATE=$(date +"%Y-%m-%dT%T" -d "1 days ago")
STARTDATE=$LASTDATE

CURRENTDATE=$(date +"%Y-%m-%dT%T")
ENDDATE=$CURRENTDATE

YEAR=${ENDDATE:0:4}

echo Downloading S2 images from $STARTDATE till $ENDDATE ...


for TILE in ${TILES[@]}

do
    QUERY="productType=S2MSI2A&startDate=$STARTDATE.000Z&completionDate=${ENDDATE}.000Z&cloudCover=[0,95]&productIdentifier=$TILE"
    echo $BASEURL$QUERY
    wget --output-document=query_$DATE_$TILE.json $BASEURL$QUERY

    #get only real product paths from json output
    jq -r  '.. | .productIdentifier? | select( . != null ) ' query_$TILE.json  | grep "/eodata/" > name_$TILE.txt

    while IFS="" read -r FILE || [ -n "$FILE" ]
    do
        echo $FILE
        SAFENAME="$(basename -- $FILE)"
        rclone copy -P -v cdse:$FILE s3allas:$BUCKETBASENAME-$YEAR-$TILE/$SAFENAME
        echo Make s3://$BUCKETBASENAME-$YEAR-$TILE/$SAFENAME public...
        s3cmd setacl --recursive --acl-public s3://$BUCKETBASENAME-$YEAR-$TILE/$SAFENAME
    done < name_$DATE_$TILE.txt
done



######################### Part 2:
# Sentinels downloaded from Allas to Puhti:
export PATH="$PATH:/scratch/project_2002694/Maria/Sentinel2"
# 

while IFS= read -r line
do
    echo "$line"
	s3cmd get --recursive --skip-existing s3://Sentinel2-MSIL2A-cloud-0-95-2024-$line
        break
done <"$file"

