"""

Script to split a shapefile with high amount of large polygons (such as all tiles covering the world) according 
to a shapefile with polygons defining the area of interest (eg field parcels) and output one shapefile with only 
large polygons covering the area of interest 

uses splitshp_functions.py

author: Samantha Wittke, FGI

31.10.2020 

"""

import os
import sys
import splitshp_functions as funcs

small_polygon_shapefile = sys.argv[1]
large_polygon_shapefile = sys.argv[2]
output_directory=sys.argv[3]

#all input shapefiles to EPSG: 4326
small_polygon_shapefile = funcs.reproject_to_epsg(small_polygon_shapefile,'4326')
large_polygon_shapefile = funcs.reproject_to_epsg(large_polygon_shapefile,'4326')

#build the output name from both input files
out_shape_name = os.path.join(output_directory, os.path.splitext(os.path.split(large_polygon_shapefile)[-1])[0] + '_' + os.path.split(small_polygon_shapefile)[-1] )

funcs.extract_needed_tiles(small_polygon_shapefile, large_polygon_shapefile, out_shape_name)
