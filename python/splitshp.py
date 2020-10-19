import os
import fiona
from shapely.geometry import shape
from copy import deepcopy
import shapeobject
from osgeo import osr
import subprocess
import sys

fullshapefile = sys.argv[1]
s2tiles = sys.argv[2]
outshpdir = sys.argv[3]

def checkProjection(myshp):
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
    if epsgcode == '3067':
        print('INFO: input shapefile has EPSG 3067, that works!')
        return myshp
    else:
        reprojectedshape = os.path.join(head, root + '_reprojected_3067'+ ext)
        if not os.path.exists(reprojectedshape):
            reprojectcommand = 'ogr2ogr -t_srs EPSG:3067 ' + reprojectedshape + ' ' + myshp
            subprocess.call(reprojectcommand, shell=True)
            print('INFO: input shapefile had other than EPSG 3067, but was reprojected and works now')
        return reprojectedshape


# bringing all input shapefiles to EPSG 3067 
fullshapefile = checkProjection(fullshapefile)
s2tiles = checkProjection(s2tiles)

#convex hull of full shapefile is created
so = shapeobject.ShapeObject(fullshapefile)
fullshapech = so.makeConvexHull().theshape
originalname = os.path.splitext(os.path.split(fullshapefile)[-1])[0]

# opening s2tiles and field parcel polygon files
with fiona.open(s2tiles,'r') as s2shp:
    with fiona.open(fullshapefile,'r') as parcelshp:

        # going through every tile in the s2tiles, open convex hull of fieldparcels, 
        # only if the tile intersects with the convex hull, check the single field parcels for intersection,
        # only if they intersect the polygon is saved in the tilebased new shapefile
        for tile in s2shp:
            with fiona.open(fullshapech,'r') as ch:
                if shape(tile['geometry']).intersects(shape(ch[0]['geometry'])):
                    tilename = tile['properties']['Name']

                    outshpname = os.path.join(outshpdir,originalname + '_' + str(tilename)+'.shp')
                    
                    driver = parcelshp.driver
                    schema = deepcopy(parcelshp.schema)
                    crs = parcelshp.crs

                    # open the new shapefile 
                    with fiona.open(outshpname, 'w', driver,schema,crs) as outputshp:
                        # going through every polygon in the fullshapefile
                        for mypoly in parcelshp:
                            
                            #print('here')
                            
                            #only if there is the polygon is intersecting the tile in question, it will be written to the new file
                            # this is the point where there may be issues if the polygon is actually a multipolygon
                            # handling multipolygons at this stage is out of scope of the code at this point so not supported
                            #if shape(mypoly['geometry']).within(shape(tile['geometry'])):
                            if shape(mypoly['geometry']).intersects(shape(tile['geometry'])):
                                print('intersection')
                                                
                                outputshp.write({                                 
                                    'properties': mypoly['properties'], 
                                    'geometry': mypoly['geometry']
                                })
                            else:
                                os.remove(outshpname)
                else:
                    print('no intersection')



                    


