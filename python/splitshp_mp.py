"""

Script to split a shapefile with small polygons (such as fieldparcels) according 
to a shapefile with large polygons (eg tile grid) and output one shapefile per large polygon 
with all small polygons that intersect with it

uses splitshp_functions.py

runs on all available cores minus 2 via multiprocessing

author: Samantha Wittke, FGI

31.10.2020 

"""

import fiona
import splitshp_functions as funcs
import sys
import multiprocessing as mp

small_polygon_shapefile = sys.argv[1]
large_polygon_shapefile = sys.argv[2]
results_directory = sys.argv[3]


# bringing all input shapefiles to EPSG 3067 
small_polygon_shapefile = funcs.reproject_to_epsg(small_polygon_shapefile,'3067')
large_polygon_shapefile = funcs.reproject_to_epsg(large_polygon_shapefile,'3067')


bounding_box_small_poly_shp = funcs.get_bounding_box(small_polygon_shapefile)

usable_number_of_cores = mp.cpu_count()-2
print(usable_number_of_cores)

pool = mp.Pool(usable_number_of_cores)

with fiona.open(large_polygon_shapefile,'r') as s2shp:
    for tile in s2shp:
        pool.apply_async(funcs.write_splitted_shapefiles, args = (bounding_box_small_poly_shp, tile, results_directory, small_polygon_shapefile))
    pool.close()
    pool.join()






                    

