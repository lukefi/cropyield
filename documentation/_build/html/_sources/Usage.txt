Usage
======

Expected Inputs
----------------

The main input to the code are a folder with Sentinel-2 data (in .SAFE format) and a folder with shapefiles that are split based on S2 tiles (for this splitshp.py can be run beforehand). The S2 folder can have all data that needs to be processed or more. If more, start and enddate of the timeframe of interest can be given to limit the data that is being processed.

Expected Outputs
----------------

Output of the process are csv files. There will be two csv files, one starting with array, one with meta per processed tile, date and band (default: 2,3,4,5,6,7,8,8A,11,12). The array file contains as many lines as there is unique IDs in the input shapefile per tile. Each line starting with the ID followed by numbers indicating the raw pixel values for the fieldparcel with that ID. The metadata file contains the ID, year, DOY, the tilefilename of S2 tile, missionID (S2A or S2B) and the count of pixel values.

Running the scripts as Puhti array job
---------------------------------------

The scripts can be run in parallel using Puhti array jobs. To do this, follow the steps below:

1. clone or copy code to Puhti ``git clone *repository link*``
2. create results folder where all results will be stored (later called **projectpath**)
3. update paths and variables in config.config (no spaces between = and texts, no ' or ", upper-/lowecase matters)

    * **startdate** for the time interval of interest (format: YYYYMMDD, eg startdate=20180418 is April, 18th in 2018)
    * **enddate** for the time interval of interest (format: YYYYMMDD)
    * **datapath** is the path where the S2 data (as .SAFE s) is stored on Puhti, eg datapath=/scratch/project\_2001107/S2L2A\_2018
    * **projectpath** is the path to where the results shall be stored (results folder created in 2.)
    * **shppath** is the path to where the shapefiles per tile are stored (specified when running splitshp.py)
    * **idname** is the name the ID-field has in the shapefile, eg idname=PlotID
    * **puhtiproject** is the name of the billing project for the array jobs, eg puhtiproject=project\_2001106
4. ``bash start_puhti.sh`` runs all scripts and outputs 2 csv files per band per tile per timepoint (one with arrays, one with metadata)
5. check that outputs have been processed


This process will create one folder for each process with a copy of the shapefile. These folders are not deleted by default, since this step can go horribly wrong. Suggestion would be to delete them manually after the jobs are done. If automatic deletion is wished. ``os.remove(jobdir)`` can be inserted into arrayextractor.py at line 88 (as part of to\_csv function. Handle with care.\\

After test running this script on Puhti actual usage of time and memory should be checked. Best to test with biggest shapefile possible. Time is set to 30 min per job as default. Memory default is 12MB. These can be changed in script puhti\_array.sh in line 5 for time (#SBATCH --time=00:30:00) and line 7 for memory (in kb; #SBATCH --mem-per-cpu=12000). Every job produces one output and one error file, these can be helpful when finding out why things went wrong if they do. However, when running a high amount of jobs, a lot of files are produced in the code directory. In line 3 and 4 the names for these files are defined. They can also be directed to a different directory which can be deleted more easily after everyhting went fine. It is also possible to not produce these files. See https://docs.csc.fi/computing/running/getting-started/ for more information. 

Running the scripts non-parallel
---------------------------------

To run the scripts non parallel eg on workstation, follow the steps below:


1. clone or copy the code to the computer
2. create results folder where all results will be stored (later called **projectpath**)
3. create anaconda environment and enter it
4. update paths and variables in config.config (no spaces between = and texts, no ' or ", upper-/lowecase matters)

    * **startdate** for the time interval of interest (format: YYYYMMDD, eg startdate=20180418 is April, 18th in 2018)
    * **enddate** for the time interval of interest (format: YYYYMMDD)
    * **datapath** is the path where the S2 data is stored , eg datapath=/home/Documents/S2L2A\_2018
    * **projectpath** is the path to where the results shall be stored (results folder created in 2.)
    * **shppath** is the path to where the shapefiles per tile are stored
    * **idname** is the name the ID-field has in the shapefile, eg idname=PlotID
    * **puhtiproject** can remain empty
    
5. ``bash start.sh`` runs all scripts and outputs 2 csv files per band per tile per timepoint (one with arrays, one with metadata)
6. check that outputs have been processed


Troubleshooting
------------------

Check carefully, that all steps above have been implemented depending on the way how the script is run (parallel/non-parallel).

| S1 file cannot be read: 
    * Check that path and filename are correct, and the file exists (>0kB), otherwise download again.

| Arrayextractor output is empty:
    * Check that the shapefile overlaps with the tile in question.

| Arrayextractor/Statistics results are all zero/NaN:
    * Check that the shapefile overlaps with the tile in question and there is data in the area of the shapefile.

Also check python packages webpages for more specific problems.

