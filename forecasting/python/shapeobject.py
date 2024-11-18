
"""
explanation
"""


import os
from osgeo import gdal, osr, ogr
from shutil import copyfile
import subprocess


class ShapeObject(object):

    def __init__(self, theshape):
        #print(theshape)
        self.theshape = theshape 
        

  
    def checkProjection(self, dependable):

        head, tail = os.path.split(self.theshape)
        root, ext = os.path.splitext(tail)
        dtail = os.path.split(dependable)[1]
        droot, dext =  os.path.splitext(dtail)
        if dext == '.shp':
            projectionfile = droot + '.prj'
            prj_file = open(projectionfile , 'r')
            prj_text = prj_file.read()
            srs = osr.SpatialReference()
            srs.ImportFromESRI([prj_text])
            srs.AutoIdentifyEPSG()
            epsgcode = srs.GetAuthorityCode(None)
            reprojectedshape = os.path.join(head, root + '_reprojected_'+epsgcode+ ext)
            if not self.theshape.endswith('reprojected_'+epsgcode+'.shp') and not os.path.exists(reprojectedshape):
                reprojectcommand = 'ogr2ogr -t_srs EPSG: '+epsgcode + reprojectedshape + ' ' + self.theshape
                subprocess.call(reprojectcommand, shell=True)
                if not os.path.exists(os.path.splitext(reprojectedshape)[0] +'.prj'):
                    copyfile(os.path.splitext(self.theshape)[0] + '.prj', os.path.splitext(reprojectedshape)[0] +'.prj' )
                #print('INFO: ' + self.theshape + ' was reprojected to EPSG code: ' + epsgcode + ' based on the projection of ' + dependable)
            if self.theshape.endswith('reprojected_' + epsgcode + '.shp'):
                return ShapeObject(self.theshape).theshape
            else:
                return ShapeObject(reprojectedshape).theshape
                
        else: #assumption: dependable is a rasterfile
            rasterfile = gdal.Open(dependable)
            rasterprojection = rasterfile.GetProjection()
            rasterrs = osr.SpatialReference(wkt=rasterprojection)
            rasterepsg = rasterrs.GetAttrValue('AUTHORITY',1)
            ##reproject the shapefile according to projection of Sentinel2/raster image
            reprojectedshape = os.path.join(head, root + '_reprojected_'+ rasterepsg+ ext)
            if not self.theshape.endswith('reprojected_'+rasterepsg+'.shp') and not os.path.exists(reprojectedshape):
                reprojectcommand = 'ogr2ogr -t_srs EPSG:'+rasterepsg+' ' + reprojectedshape + ' ' + self.theshape
                subprocess.call(reprojectcommand, shell=True)
                if not os.path.exists(os.path.splitext(reprojectedshape)[0] +'.prj'):
                    copyfile(os.path.splitext(self.theshape)[0] + '.prj', os.path.splitext(reprojectedshape)[0] +'.prj' )
                #print('INFO: ' + self.theshape + ' was reprojected to EPSG code: ' + rasterepsg + ' based on the projection of ' + dependable)
            if self.theshape.endswith('reprojected_' + rasterepsg + '.shp'):
                return ShapeObject(self.theshape).theshape
            else:
                return ShapeObject(reprojectedshape).theshape


    def makeConvexHull(self):
        # Get a Layer
        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(self.theshape, 0)
        inLayer = inDataSource.GetLayer()

        # Collect all Geometry
        geomcol = ogr.Geometry(ogr.wkbGeometryCollection)
        for feature in inLayer:
            geomcol.AddGeometry(feature.GetGeometryRef())

        # Calculate convex hull
        convexhull = geomcol.ConvexHull()

        # Save extent to a new Shapefile
        convexhullp = os.path.splitext(self.theshape)[0] + '_convexhull.shp'
        outDriver = ogr.GetDriverByName("ESRI Shapefile")
        copyfile(os.path.splitext(self.theshape)[0] + '.prj', os.path.splitext(convexhullp)[0] + '.prj' )

        # Remove output shapefile if it already exists
        if os.path.exists(convexhullp):
            outDriver.DeleteDataSource(convexhullp)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(convexhullp)
        outLayer = outDataSource.CreateLayer("convexhull", geom_type=ogr.wkbPolygon)

        # Add an ID field
        idField = ogr.FieldDefn("ID", ogr.OFTInteger)
        outLayer.CreateField(idField)

        # Create the feature and set values
        featureDefn = outLayer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(convexhull)
        feature.SetField("ID", 1)
        outLayer.CreateFeature(feature)
        feature = None

        # Save and close DataSource
        inDataSource = None
        outDataSource = None

        return ShapeObject(convexhullp)
