"""
2024-01-31 MY




RUN:

python 00B-yield-region-and-maps.py -c 1310 \
-i /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2015_2023.csv \
-o /Users/myliheik/Documents/myCROPYIELD/maakuntaYields/ \
-s /Users/myliheik/Documents/GISdata/Kasvulohkot2020/kasvulohkot2020-mod.shp

WHERE:
-i: inputpath to predictions
-c: crop type(s)
-o: outputpath to yield files and images
-s: shapefile of annual parcel data, year info included
-r: region, by default: maakunta

Works for 1310, 1320, 1400, 1110, 1120, 4210, 1230, or 3000.

"""

import pandas as pd 
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.colors as mcolors

import matplotlib.cm as cm

from matplotlib.lines import Line2D

import numpy as np
import shapely

from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as mpatches

from matplotlib.colors import ListedColormap, LinearSegmentedColormap, TwoSlopeNorm

from pathlib import Path
import argparse
import textwrap
import math

import warnings
warnings.filterwarnings("ignore")

#def round_up(n, decimals=0):
#    multiplier = 10 ** decimals
#    return math.ceil(n * multiplier) / multiplier

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

# EDIT: 
#Europe borders:
fpeuropa = '/Users/myliheik/Documents/GISdata/EU-countries/Europe_borders.shp'


    
def readShapefile(shapefp):
        gdf = gpd.read_file(shapefp)
        #print(gdf.columns)
        gdf.rename(columns = {'MAATILA_TUNNUS': 'MAATILA_TU', 'PLVUOSI_PERUSLOHKOTUNNUS': 'PLVUOSI_PE', 'KLILM_TUNNUS': 'KLILM_TUNN', 'KVI_KASVIKOODI': 'KVI_KASVIK'}, inplace = True)
        gdf['parcelID'] = gdf['MAATILA_TU'].astype(str) + '_' + gdf['PLVUOSI_PE'].astype(str) + '_' + gdf['KLILM_TUNN'].astype(str)
        gdf['keskipiste'] = gdf.centroid
        year = gdf['VUOSI'][0]
        
        return gdf, year


def readYields(inputfile, croptype, year):
        df0 = pd.read_csv(inputfile)
        df = df0[df0['VUOSI'] == year]
        
        if croptype == '1310': harvested = 'rehuohra_ala'; cropname = 'Feed-barley'; totalyield = 'rehuohra_sato'
        elif croptype == '1320': harvested = 'mallasohra_ala'; cropname = 'Malting-barley'; totalyield = 'mallasohra_sato'
        elif croptype == '1400': harvested = 'kaura_ala'; cropname = 'Oats'; totalyield = 'kaura_sato'
        elif croptype == '1110': harvested = 'syysvehna_ala'; cropname = 'Winter-wheat'; totalyield = 'syysvehna_sato'
        elif croptype == '1120': harvested = 'kevatvehna_ala'; cropname = 'Spring-wheat'; totalyield = 'kevatvehna_sato'
        elif croptype == '4200': harvested = 'rapsi_ala'; cropname = 'Oil-seed-rape'; totalyield = 'rapsi_sato'
        #elif croptype == '4100': harvested = 'rypsi_ala'; cropname = 'Turnip-rape'; totalyield = 'rypsi_sato'

        elif croptype == '1230': harvested = 'ruis_ala'; cropname = 'Rye'; totalyield = 'ruis_sato'
     
        elif croptype == '3100': harvested = 'peruna_ala_yht'; cropname = 'Potato'; totalyield = 'peruna_sato_yht'
        elif croptype == '': harvested = 'kuivaheina_ala'; cropname = 'kuivaheina_ala'; totalyield = 'kuivaheina_sato'
        elif croptype == '': harvested = 'sailorehu_tuore_ala'; cropname = 'sailorehu_tuore_ala'; totalyield = 'sailorehu_tuore_sato'
        elif croptype == '': harvested = 'sailorehu_esik_ala'; cropname = 'sailorehu_esik_ala'; totalyield = 'sailorehu_esik_sato'
        elif croptype == '': harvested = 'niittorehu_ala'; cropname = 'niittorehu_ala'; totalyield = 'niittorehu_sato'
        else:
            print(f'Crop type {croptype} not found! Should be either 1310, 1320, 1400, 1110, 1120, 4210, 1230, or 3000.')
            
        print(f'Crop type is {cropname}')

        df2 = df.dropna(subset = [harvested, totalyield])     
        
        df2['yield'] = round(df2[totalyield] / (df2[harvested]/100),0) # kg / (a/100 -> ha)

        return df2, cropname
    

def mergeData(gdf, df2, croptype, yieldpath, cropname, year, region):
        if croptype == '3100': # potatoes
            gdf2 = gdf[gdf['KVI_KASVIK'].str.startswith('31')]
        else: 
            gdf2 = gdf[gdf['KVI_KASVIK'] == croptype]       
            
        # Choose only farms in survey data:

        gdf2.MAATILA_TU = gdf2.MAATILA_TU.astype('int').copy()
        row_mask = gdf2.MAATILA_TU.isin(df2['tiltu'].unique().tolist())
        filtered = gdf2[row_mask].copy()   
            
        ####### Discard farms having fields further than 30km apart:
        
        dataByFarm = filtered[['MAATILA_TU', 'KVI_KASVIK', 'geometry']].dissolve(by=['MAATILA_TU', 'KVI_KASVIK'], aggfunc='sum')
        farms0 = len(dataByFarm)

        distanceWithin = dataByFarm.geometry.bounds
        distanceWithin['distancex'] = distanceWithin.maxx - distanceWithin.minx
        distanceWithin['distancey'] = distanceWithin.maxy - distanceWithin.miny
        distanceWithin['maxdistance'] = distanceWithin[['distancex', 'distancey']].apply(max, axis=1)
        distanceWithin['maxdistance'].describe() # keskim. 3.9km, max 136km
        dataByFarm2 = dataByFarm[distanceWithin['maxdistance'] < 30000].reset_index()
        farms1 = len(dataByFarm2)        
        
        row_mask = filtered.MAATILA_TU.isin(dataByFarm2['MAATILA_TU'])
        filtered1 = filtered[row_mask].copy()
        
        print(f'{(farms1-farms0)} farms filtered out because their fields were > 30km apart.') 
        
        ##############################################################

        filtered2 = filtered1.merge(df2[['tiltu', 'yield']], how = 'left', left_on = 'MAATILA_TU', right_on = 'tiltu')
        filtered3 = filtered2.dropna(subset = ['yield'])
        filtered3['lon'] = filtered3.keskipiste.x
        filtered3['lat'] = filtered3.keskipiste.y
                
        ### Overlay with region:
        # luetaan rajat:
        if region == 'maakunta':
            fp = "/Users/myliheik/Documents/GISdata/mml/hallintorajat_milj_tk/Hallintorajat2020-teemakartoille-ei-merialueita/maakunnat_2020_milj.shp"
        elif region == 'kunta':
            fp = "/Users/myliheik/Documents/GISdata/mml/hallintorajat_milj_tk/Hallintorajat2020-teemakartoille-ei-merialueita/kunnat_2020_milj.shp"

        gdfmaakunta = gpd.read_file(fp)
        gdfmaakunta['NATCODE'] = gdfmaakunta['NATCODE'].astype('int')

        # haetaan satolohkoille maakuntatieto:
        filtered33 = gpd.overlay(filtered3, gdfmaakunta, how='intersection')   

        
        
        ###
        # more than 5 observations from a grid
        filtered33['count'] = filtered33[['NATCODE', 'parcelID']].groupby('NATCODE')['parcelID'].transform('count')
        filtered4 = filtered33[filtered33['count'] > 5]   

        # Weighted mean:
        filtered4['tmp_weighted_yield'] = filtered4['yield'] * filtered4['PINTAALA']

        filtered5 = filtered4[['NATCODE', 'tmp_weighted_yield', 'PINTAALA']].groupby('NATCODE').agg('sum')
        filtered5['weighted_yield'] = filtered5['tmp_weighted_yield'] / filtered5['PINTAALA']
        
        filtered5['weighted_yield'] = round(filtered5['weighted_yield'],0)

        if type(year) is not int: # check
            year = int(year)  
            
        outputfile = os.path.join(yieldpath, 'Yields-' + croptype + '-' + cropname + '-' + str(year) + '.csv')
        print(f"Saving yields in {outputfile}")
        filtered5[['weighted_yield']].to_csv(outputfile, index = True)
        
        gdfmaakunta2 = gdfmaakunta.set_index('NATCODE')
        # merge:
        filtered6 = pd.concat([gdfmaakunta2, filtered5[['weighted_yield']]], axis = 1)
        
        return filtered6
    
    
def plotMaps(FIyields, croptype, cropname, year, imagepath, dfeuropaFIN, region):

    miny = 6632470
    maxy = 7400000
    
    plt.rcParams['text.usetex'] = True

    if type(year) is not int: # check
        year = int(year)
 
    # define min and max values and colormap for the plots
    if croptype == '3100':
        value_min = 10000
        value_max = 30000       
    else:
        value_min = 1000
        value_max = 5000
    cmap = 'YlGn'
    norm = mcolors.Normalize(vmin = value_min, vmax = value_max)
    
    fig = plt.figure(figsize = (6,10))
    ax_map = fig.add_axes([0, 0, 1, 1])
    dfeuropaFIN.plot(ax = ax_map, color = 'lightgray')#, color=colors) #['#C62828', '#283593', '#283593', '#FF9800'])
    ax_map.set_axis_off()

    #gdf = gpd.GeoDataFrame(FIyields, geometry = gpd.points_from_xy(FIyields['EOFORIGIN10km'], FIyields['NOFORIGIN10km']), crs = 'EPSG:3067')

    FIyields.plot(ax = ax_map, column = 'weighted_yield', marker = 's', markersize = 25, # marker = 'o' for bullet
                       vmin = value_min, vmax = value_max, cmap = cmap, norm = norm, edgecolor = None)

    ax_map.axis('off')
    #ax_map.set(title = cropname + ' ' + year)

    ax_map.annotate('Mean weighted yield: ' + str(round(FIyields['weighted_yield'].mean())) + ' kg/ha',
        xy=(596327, 6823806),  xycoords='data', weight='bold',
    xytext=(0.35, 0.55), textcoords='axes fraction', # xytext=(0.95, 0.55)
    #arrowprops=dict(facecolor='black', shrink=0.05),
    horizontalalignment='right', verticalalignment='top',
    )


    # define a mappable based on which the colorbar will be drawn
    mappable = cm.ScalarMappable(
        norm = mcolors.Normalize(vmin = value_min, vmax = value_max),
        cmap = cmap
    )

    # define position and extent of colorbar
    #cb_ax = fig.add_axes([0.1, 0.1, 0.8, 0.05]) # horizontal
    cb_ax = fig.add_axes([1, .1, 0.025, 0.85])

    ax_map.set_title('Yields of ' + cropname + ' (' + str(year) + ') by regions (' + region + ')')
    # draw colorbar
    cbar = fig.colorbar(mappable, cax = cb_ax, orientation='vertical', label =  'Yield (kg/ha)')

    outfile = os.path.join(imagepath, 'Yields-' + croptype + '-' + cropname + '-' + str(year) + '-' + region + '.png')
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    print(f"Saving image in {outfile}")


    
    

    
    

# MAIN:
def main(args):
    try:
        if not args.inputfile or not args.crops or not args.shapefile:
            raise Exception('Missing input filepath or crop type argument. Try --help .')

        print(f'\n00B-yield-region-and-maps.py')
        
        
        imagepath = Path(os.path.expanduser(args.outputpath), 'img')
        imagepath.mkdir(parents=True, exist_ok=True)

        yieldpath = Path(os.path.expanduser(args.outputpath), 'yields')
        yieldpath.mkdir(parents=True, exist_ok=True)
        
        dfeuropa = gpd.read_file(fpeuropa)
        dfeuropaFIN = dfeuropa[(dfeuropa['TZID'] == 'Europe/Helsinki') | (dfeuropa['TZID'] == 'Europe/Mariehamn')].to_crs('epsg:3067')           
        
        gdf, year = readShapefile(args.shapefile)
        
        for croptype in args.crops:
            
            df2, cropname = readYields(args.inputfile, croptype, year)
            
            FIyields = mergeData(gdf, df2, croptype, yieldpath, cropname, year, args.region) 
                        
            print(f'Do a map of {cropname}')
            plotMaps(FIyields, croptype, cropname, year, imagepath, dfeuropaFIN, args.region)
        
        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write output. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputfile',
                        help='Filepath of raw yields.',
                        type=str)  
    parser.add_argument('-s', '--shapefile',
                        help='Filepath of shapefile containing parcel geometries.',
                        type=str)  
    parser.add_argument('-o', '--outputpath',
                        help='Filepath of outputs.',
                        type=str)  
    parser.add_argument('-c', '--crop', action='store', dest='crops',
                         type=str, nargs='*', default=['1310', '1320', '1400'],
                         help='Crop type(s). E.g. -c 1310 1320')    
    parser.add_argument('-r', '--region', default = 'maakunta',
                         help='Region: kunta or maakunta? Default: maakunta.',
                       type=str)    

    args = parser.parse_args()
    main(args)
