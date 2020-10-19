Additional scripts
==================

splitshp.py
------------


This script has to be run separately before running the main script (above) if only one huge shapefile is available. It takes three input arguments which are given as command line arguments.
The script will take the input shapefile that spreads over multiple Sentinel-2 tiles and split the shapefile into several per tile shapefiles.
All polygons that are intersecting a tile will be part of the new tile based shapefile.
The script is called with 
``pyhton splitshp.py [1] [2] [3]``
| with 

* [1] being the path to the full shapefile, 
* [2] being the shapefile with S2tiles  
* [3] the path to the folder where results shall be stored

| Example call:  

``python splitshp.py /home/samu/Documents/cropyield/cropyield.shp /home/samu/Documents/cropyield/Sentinel2_tiles_world.shp /home/samu/Documents/cropyield/results``

The output of running this script is multiple shapefiles withing the given results folder (no subdirectories). Each shapefile (also auxiliary files, like .shx, .prj, .dbf) has the name of the original shapefile plus underscore tilename before the extension. Example: The original shapefile was called cropyield2018.shp, then the resulting files would be called cropyield2018\_35VHN.shp, cropyield\_34WMH.shp, etc.
When not using the splitshp.py for splitting, it is essential that the last part before the extension has the tilename in that format, otherwise the code gets confused. If one needs to process several different shapefiles, the results should be split in separate folders. Every shape folder that becomes an input to the main code, can only have same basename (in the example cropyield2018) plus the different tile names.



histogramize.py
-----------------

This script is run separately after the main script run, it takes as input the directory of array csv files, calculates histograms for each ID with given
number of bins. Output is same amount of csv files with histograms instead of pixel value arrays. First value in every row is the field parcel ID.
The script is called with 
``python histogramize.py [1] [2] [3]``

| with 

* [1] being the path to the folder with array csv files, 
* [2] being the number of bins for the histogram and 
* [3] the percentage of how much of the extremes (high and low) should be removed. 

| Example call: 

``python histogramize.py /home/samu/Documents/cropyield/results 10 0.1``




