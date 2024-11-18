"""
2024-01-31 MY




RUN:

python 00C-longTerm-yield-region-and-maps.py \
-i /Users/myliheik/Documents/myCROPYIELD/griddedYields/yields/ \
-o /Users/myliheik/Documents/myCROPYIELD/griddedYields/longTermYields/ \
-r grid

WHERE:
-i: inputpath to directory with annual yields 
-o: outputpath to long term yield files and images
-r: region, by default: maakunta

Works for all crops in the input directory.

"""

import pandas as pd 
import geopandas as gpd # needed for maps
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
import matplotlib.colors as mcolors

import matplotlib.cm as cm

from matplotlib.lines import Line2D

import numpy as np

from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as mpatches

from matplotlib.colors import ListedColormap, LinearSegmentedColormap, TwoSlopeNorm

from pathlib import Path
import argparse
import textwrap
import math

import warnings
warnings.filterwarnings("ignore")


# EDIT: 
#Europe borders:
fpeuropa = '/Users/myliheik/Documents/GISdata/EU-countries/Europe_borders.shp'


        

    
    
def plotMaps(FIyields, croptype, cropname, imagepath, years, dfeuropaFIN, region):

    miny = 6632470
    maxy = 7400000
    
    plt.rcParams['text.usetex'] = True
 
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

    if region == 'grid':
        gdf2 = gpd.GeoDataFrame(FIyields, geometry = gpd.points_from_xy(FIyields['EOFORIGIN10km'], FIyields['NOFORIGIN10km']), crs = 'EPSG:3067')
    else:
        if region == 'maakunta':
            fp = "/Users/myliheik/Documents/GISdata/mml/hallintorajat_milj_tk/Hallintorajat2020-teemakartoille-ei-merialueita/maakunnat_2020_milj.shp"
        elif region == 'kunta':
            fp = "/Users/myliheik/Documents/GISdata/mml/hallintorajat_milj_tk/Hallintorajat2020-teemakartoille-ei-merialueita/kunnat_2020_milj.shp"
        else:
            print('Unknown region id. Please, select either kunta, maakunta, or grid (10km)')
        gdf = gpd.read_file(fp)
        gdf['NATCODE'] = gdf['NATCODE'].astype('int')
        gdf2 = gdf.merge(FIyields)
        gdf2['yield'] = gdf2['weighted_yield']
      
    gdf2.plot(ax = ax_map, column = 'yield', marker = 's', markersize = 25, # marker = 'o' for bullet
                       vmin = value_min, vmax = value_max, cmap = cmap, norm = norm, edgecolor = None)

    ax_map.axis('off')
    #ax_map.set(title = cropname + ' ' + year)

    ax_map.annotate('Mean yield: ' + str(round(gdf2['yield'].mean())) + ' kg/ha',
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

    ax_map.set_title('Long term yields of ' + cropname.replace('-', ' ') + ' (' + years + ') by regions (' + region + ')')
    # draw colorbar
    cbar = fig.colorbar(mappable, cax = cb_ax, orientation='vertical', label =  'Yield (kg/ha)')

    outfile = os.path.join(imagepath, 'Yields-' + croptype + '-' + cropname + '-' + region + '.png')
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    print(f"Saving image in {outfile}")


    
    

    
    

# MAIN:
def main(args):
    try:
        if not args.inputpath:
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n00C-longTerm-yield-region-and-maps.py')
        
        
        outputpath = Path(os.path.expanduser(args.outputpath), 'img')
        outputpath.mkdir(parents=True, exist_ok=True)

        imgpath = Path(os.path.expanduser(args.outputpath), 'img')
        imgpath.mkdir(parents=True, exist_ok=True)
        
        dfeuropa = gpd.read_file(fpeuropa)
        dfeuropaFIN = dfeuropa[(dfeuropa['TZID'] == 'Europe/Helsinki') | (dfeuropa['TZID'] == 'Europe/Mariehamn')].to_crs('epsg:3067')           
                
            
        inputpath2 = args.inputpath + 'Yields*.csv'

        crops = []
        for filename in glob.glob(inputpath2):
            crops.append(os.path.basename(filename).split('-')[1])

        uniqueCrops = sorted(set(crops))

        for crop in uniqueCrops:
            inputpath3 = args.inputpath + 'Yields-' + crop + '*.csv'
            filepaths = glob.glob(inputpath3)
     
            # min-max years:
            allyears = []
            for filename in filepaths:
                allyears.append(int(os.path.basename(filename).split('-')[-1].replace('.csv', '')))

            years = str(min(allyears)) + '-' + str(max(allyears))

            if crop == '1310':  cropname = 'feed-barley'
            elif crop == '1320':  cropname = 'malting-barley'
            elif crop == '1400': cropname = 'oats'
            elif crop == '1110':  cropname = 'winter-wheat'
            elif crop == '1120':  cropname = 'spring-wheat'
            elif crop == '4200':  cropname = 'oil-seed-rape'
            #elif crop == '4100':  cropname = 'turnip-rape'

            elif crop == '1230': cropname = 'rye'

            elif crop == '3100': cropname = 'potato'
            elif crop == '': cropname = 'kuivaheina_ala'
            elif crop == '': cropname = 'sailorehu_tuore_ala'
            elif crop == '': cropname = 'sailorehu_esik_ala'
            elif crop == '': cropname = 'niittorehu_ala'
            else:
                print(f'Crop type {crop} not found! Should be either 1310, 1320, 1400, 1110, 1120, 4210, 1230, or 3000.')

            print(f'Crop type is {cropname}')
        
            df = pd.concat(map(pd.read_csv, filepaths))
            if args.region == 'grid':
                df.groupby('10kmCELLCODE').mean('yield').to_csv(os.path.join(outputpath, 'Yields-' + crop + '.csv'), index = True)
            else:
                round(df.groupby('NATCODE').mean('weighted_yield'), 0).to_csv(os.path.join(outputpath, 'Yields-' + crop + '.csv'), index = True)
                
            print(f"Saving long term yields into {os.path.join(outputpath, 'Yields-' + crop + '.csv')}")

            print(f'\nDoing a map of {cropname}...')
            plotMaps(df, crop, cropname, imgpath, years, dfeuropaFIN, args.region)

        
        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write output. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputpath',
                        help='Filepath to directory of yields.',
                        type=str)  
    parser.add_argument('-o', '--outputpath',
                        help='Filepath of outputs.',
                        type=str)  
    parser.add_argument('-r', '--region', default = 'maakunta',
                         help='Region: kunta or maakunta? Default: maakunta.',
                       type=str)    

    args = parser.parse_args()
    main(args)
