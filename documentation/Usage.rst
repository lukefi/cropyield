Usage
======

Users will need some level of understanding of geoinformatics and computing systems to be able to run the scripts. 

Expected Inputs
----------------

The main input to the code are a folder with Sentinel-2 data (in .SAFE format) and a folder with shapefiles that are split based on S2 tiles (for this, splitshp_world.py can be run beforehand). The S2 folder can have all data that needs to be processed or more. If more, start and enddate of the timeframe of interest can be given to limit the data that is being processed.

Expected Outputs
----------------

Output of the process are csv files. There will be two csv files, one starting with **array**, one with **meta** per processed tile, date and band (default: 2,3,4,5,6,7,8,8A,11,12). The array file contains as many lines as there is unique IDs in the input shapefile per tile. Each line starting with the ID followed by numbers indicating the raw pixel values for the fieldparcel with that ID. The metadata file contains the ID, year, DOY, the tilefilename of S2 tile, missionID (S2A or S2B) and the count of pixel values.

Running the scripts 
--------------------

To run the scripts non parallel eg on workstation, follow the steps below:


1. clone or copy the code to the computer
2. create results folder where all results will be stored (later called **projectpath**)
3. create anaconda environment and activate it
4. create a file called config.config within python directory and fill it with the following information (no spaces between = and texts, no ' or ", upper-/lowecase matters)

    * **startdate** for the time interval of interest (format: YYYYMMDD, eg startdate=20180418 is April, 18th in 2018)
    * **enddate** for the time interval of interest (format: YYYYMMDD)
    * **datapath** is the path where the S2 data is stored , eg datapath=/home/Documents/S2L2A\_2018
    * **projectpath** is the path to where the results shall be stored (results folder created in 2.)
    * **shppath** is the path to where the shapefiles per tile are stored
    * **idname** is the name the ID-field has in the shapefile, eg idname=PlotID
    
5. ``bash start.sh`` runs all scripts and outputs 2 csv files per band per tile per timepoint (one with arrays, one with metadata)
6. check that outputs have been processed


Troubleshooting
------------------

Check carefully, that all steps above have been implemented.

| Rasterfile cannot be read: 
    * Check that path and filename are correct, and the file exists (>0kB), otherwise download again.

| Arrayextractor output is empty:
    * Check that the shapefile overlaps with the tile in question.

| Arrayextractor/Statistics results are all zero/NaN:
    * Check that the shapefile overlaps with the tile in question and there is data in the area of the shapefile.

Also check python packages webpages for more specific problems.

