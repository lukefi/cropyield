'''

script to do the array extraction based on userinput
type 'python arrayextractor.py -h' for list of possible inputs
minimum input: -f, -shp, -p, -id 
output: a csv file with pixelvalues within polygons (one row per polygon), polygon shape is not preserved 

'''

import os
from rasterstats import zonal_stats
import shapeobject
import numpy as np
import csv
import userinput
from datetime import datetime
from shutil import copyfile
import sys

#direct array extraction

def main():

    ui = userinput.UserInput()
    jobnumber = ui.jobnumber
    bandpathtxt = ui.bandpath
    btxt= os.path.split(bandpathtxt)[-1]
    tile = btxt.split('_')[0][1:]
    print(tile)
    #/scratch/project_2001106/S2L2A_2018/T35VMK/S2A_MSIL2A_20180811T095031_N0208_R079_T35VMK_20180811T124846.SAFE/GRANULE/
    # L2A_T35VMK_A016378_20180811T095029/IMG_DATA/R10m/T35VMK_20180811T095031_B04_10m.jp2

    shapedir = ui.shapedir
    namelist = os.listdir(shapedir)[0].split('_')
    shapename = '_'.join(namelist[:-1])
    tileshapename = shapename + '_' + tile
    shapefile = os.path.join(shapedir, tileshapename)
    projectname = ui.projectname
    if not jobnumber is None:
        for ext in ['.shp','.shx','.prj','.dbf']:
            shp = shapefile + ext
            if os.path.isfile(shp):
                print(shp)
                jobdir = os.path.join(projectname,jobnumber)
                dst = os.path.join(jobdir,tileshapename+ext)
                if not os.path.exists(jobdir):
                    os.makedirs(jobdir)
                copyfile(shp, dst)
                if dst.endswith('.shp'):
                    shpfile = dst
    else:
        shpfile = shapefile + '.shp'
    shapeobj = shapeobject.ShapeObject(shpfile)
    shpfile = shapeobj.checkProjection(bandpathtxt)
    
    extractarray(bandpathtxt,shpfile,tile,projectname, ui)

        

def extractarray(rasterpath ,shpfile,tile,projectname, ui):

    date = os.path.split(rasterpath)[-1].split('_')[1][:8]
    band = os.path.splitext(os.path.split(rasterpath)[-1])[0].split('_')[-2]

    print('arrayextractor started')

    a=zonal_stats(shpfile, rasterpath, stats=['mean'], band=1, geojson_out=True, all_touched=False, raster_out=True, nodata=np.nan)

    myarrays = []

    for x in a:
        myarray = x['properties']['mini_raster_array']
        myarray = myarray.filled(-9999)
        myarray = myarray[myarray != -9999]
        myarray = myarray.flatten()
        if np.count_nonzero(myarray) == 0:
            continue
        count = len(myarray)
  
        myid = [x['properties'][ui.idname]]
        arr = myarray.tolist()
        myid.extend(arr)
        arr = myid
        
        meta = extractmeta(rasterpath, myid[0], date, count, projectname, band, tile)
        
        myarrays.append(arr)
    
    tocsv(date,band,myarrays,tile,projectname)


def tocsv(date,band,myarray,tile,projectname):
    
    csvfile = os.path.join(projectname,'array_'+tile + '_' + date +'_'+ band+'.csv')
    with open(csvfile, "w") as f:
        writer = csv.writer(f)
        writer.writerows(myarray)


def extractmeta(bandtif, parcelID, mydate, count, projectname, band, tile):

    #(parcel_ID, year, day-of-year, name of the file (tile), mission ID (SA|SB), count)

    #band and tile could be gotten from bandtif
     
    metadatacsv =  os.path.join(projectname,'meta_'+tile + '_' + mydate +'_'+ band+'.csv')

    mycolumns = ['PlotID','year','DOY','tilefilename','missionID','count']

    if not os.path.exists(metadatacsv): # write the header
        with open(metadatacsv,'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(mycolumns)
    
    year = mydate[0:4]

    dateobj = datetime.strptime(mydate, '%Y%m%d')
    doy = (dateobj - datetime(dateobj.year, 1, 1)).days + 1

    bandtif = bandtif.split('/')[-6]
    tilefilename = ('_').join(bandtif.split('_')[0:6])
    
    missionID = bandtif.split('_')[0]

    onerow = [parcelID, year, doy, tilefilename, missionID, count]

    with open(metadatacsv,'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(onerow)
        


if __name__ == "__main__":
    main()
