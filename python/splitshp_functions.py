"""

Collection of functions related to the splitting of a shapefile based on another shapefile

author: Samantha Wittke, FGI

31.10.2020

"""


import os
import shapely
import fiona
from shapely.geometry import shape, Polygon
from copy import deepcopy
from osgeo import osr
import subprocess


def reproject_to_epsg(myshp,myepsg):
    print('INFO: checking the projection of the inputfile now')
    head, tail = os.path.split(myshp)
    root, ext = os.path.splitext(tail)
    rootprj = root + '.prj'
    projectionfile = os.path.join(head, rootprj)
    prj_file = open(projectionfile , 'r')
    prj_text = prj_file.read()
    srs = osr.SpatialReference()
    srs.ImportFromESRI([prj_text])
    srs.AutoIdentifyEPSG()
    epsgcode = srs.GetAuthorityCode(None)
    if epsgcode == myepsg:
        print('INFO: input shapefile has EPSGmyepsg that works!')
        return myshp
    else:
        reprojectedshape = os.path.join(head, root + '_reprojected_' + myepsg +  ext)
        if not os.path.exists(reprojectedshape):
            reprojectcommand = 'ogr2ogr -t_srs EPSG:' + myepsg + ' ' +  reprojectedshape + ' ' + myshp
            print(reprojectcommand)
            subprocess.call(reprojectcommand, shell=True)
            print('INFO: input shapefile had other than EPSG ' + myepsg + ' but was reprojected and works now')
        return reprojectedshape

def get_parameter_content(polygon, parameter):
    return polygon[parameter]

def make_geometryobject(parameter_content):
    return shape(parameter_content)

def get_shp_properties(shapefile):
    driver = shapefile.driver
    schema = deepcopy(shapefile.schema)
    crs = shapefile.crs
    return driver,schema,crs

def get_bounding_box(shapefile):
    with fiona.open(shapefile,'r') as open_shp:
        bounding_box_coordinates = open_shp.bounds
        print(bounding_box_coordinates)
    return Polygon.from_bounds(bounding_box_coordinates[0], bounding_box_coordinates[1], bounding_box_coordinates[2], bounding_box_coordinates[3] )


def write_splitted_shapefiles(bounding_box_small_poly_shp,tile,outshpdir, small_poly_shp):
    
    one_tile_geometry = make_geometryobject(get_parameter_content(tile,'geometry'))
    if one_tile_geometry.intersects(bounding_box_small_poly_shp):
        tilename = tile['properties']['Name']

        originalname = os.path.splitext(os.path.split(small_poly_shp)[-1])[0]
        outshpname = os.path.join(outshpdir,originalname + '_' + str(tilename)+'.shp')

        with fiona.open(small_poly_shp,'r') as smaller_open_shp:
            driver,schema,crs = get_shp_properties(smaller_open_shp)

            # open the new shapefile 
            with fiona.open(outshpname, 'w', driver,schema,crs) as outputshp:
                for small_polygon in smaller_open_shp:
                    small_polygon_geometry = get_parameter_content(small_polygon, 'geometry')
                    if not small_polygon_geometry is None:
                        #only if there is the polygon is intersecting the tile in question, it will be written to the new file
                        # this is the point where there may be issues if the polygon is actually a multipolygon
                        # handling multipolygons at this stage is out of scope of the code at this point so not supported
                        #if shape(small_polygon['geometry']).within(one_tile_geometry):
                        if make_geometryobject(small_polygon_geometry).intersects(one_tile_geometry):                
                            outputshp.write({                                 
                                'properties': small_polygon['properties'], 
                                'geometry': small_polygon['geometry']})

def extract_needed_tiles(small_poly_shp, large_poly_shp, outshpname):

    bounding_box_small_poly_shp = get_bounding_box(small_poly_shp)

    with fiona.open(large_poly_shp,'r') as s2shp:
        driver,schema,crs = get_shp_properties(s2shp)

        with fiona.open(outshpname, 'w', driver,schema,crs) as outputshp:
            for tile in s2shp:
                one_tile_geometry = make_geometryobject(get_parameter_content(tile,'geometry'))
                if one_tile_geometry.intersects(bounding_box_small_poly_shp):
                    outputshp.write({                                 
                        'properties': tile['properties'], 
                        'geometry': tile['geometry']})