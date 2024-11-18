"""
2024-07-16 MY make yield maps

RUN:

python 20-make-maps-Finnish.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/2024-07-15/ \
-r gridded

WHERE:
-i: inputpath to predictions, reads all crops
-r: region

Note: toimii komentoriviltä, mutta huom! ei Notebookissa (Puhti), jotain matplotlib ongelmaa.


"""


import utils
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
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)

from pathlib import Path
import argparse
import textwrap
import datetime
import glob

import warnings
warnings.filterwarnings('ignore')

import boto3

my_bucketname = 'satoennusteet2024'

# EDIT: 
#Europe borders:
fpeuropa = '/projappl/project_2009889/metadata/EU-countries/Europe_borders.shp'
# 
fpLongTermNational = '/projappl/project_2009889/metadata/nationalYields/longTerm'
# metafile:
metafilefp = '/scratch/project_2009889/cropyield2024/forecasting/shpfiles/forecasting-2024/metafile-2024.csv'

def readNationalYields(inputpath): # predicted
        inputfile = os.path.join(inputpath, 'yields.csv')
        df = pd.read_csv(inputfile, delimiter = ' ', header = None)        
        df['Year'] = df[7] 
        df['Yield'] = df[8] 
        df['Crop'] = df[5] 

        return df
    
def readLongtermNationalYields(crop):
        for inputfile in os.listdir(fpLongTermNational):
            #print(crop)
            if str(crop) in inputfile:
                #print(inputfile)
                df = pd.read_csv(os.path.join(fpLongTermNational, inputfile))
                longTermYield = df['weighted_yield']
            else:
                print(f'Did not find long term national yields for {crop}')
                longTermYield = None
            
        return longTermYield

def readLongtermNationalYields(crop):
        longTermYield = None
        if crop == '1310': 
            filename = os.path.join(fpLongTermNational, 'National-1310-feed-barley.csv')        
        elif crop == '1320':
            filename = os.path.join(fpLongTermNational, 'National-1320-malting-barley.csv')  
        elif crop == '1400':
            filename = os.path.join(fpLongTermNational, 'National-1400-oats.csv')  
        elif crop == '1110':
            filename = os.path.join(fpLongTermNational, 'National-1110-winter-wheat.csv')  
        elif crop == '1120':
            filename = os.path.join(fpLongTermNational, 'National-1120-spring-wheat.csv')  
        elif crop == '1230':
            filename = os.path.join(fpLongTermNational, 'National-1230-rye.csv')  
        else:
            filename = None
            
        if filename:
            df = pd.read_csv(filename)
            #print(df)
            longTermYield = df['weighted_yield'][0]

        else:
            print(f'Did not found national long term yields for {crop}...')
        
        return longTermYield

    

def readYields(inputpath, crop, year):
        inputfile = os.path.join(inputpath, crop + '-' + year, 'TCNPreds-FI.csv')
        df = pd.read_csv(inputfile)        
        df22 = df['parcelID'].str.split('_', expand = True)
        df['Year'] = df22[0]
        df['Municipality'] = df22[2]
        df['Crop'] = df22[3] # need for merging

        return df

def plotMaps(longTermNationalYield, nationalPred, data, crop, imagepath, dfeuropaFIN, pvm, pvm00, region):

    deviationNational = round(((nationalPred - longTermNationalYield)/ longTermNationalYield) * 100, 0).astype(int)
    if deviationNational > 0:
        deviationNationaltxt = '+' + str(deviationNational)
    else:
        deviationNationaltxt = str(deviationNational)
    
    miny = 6632470
    maxy = 7400000
    
    if crop == '1310': 
        viljanimi = 'Rehuohra'        
    elif crop == '1320':
        viljanimi = 'Mallasohra'
    elif crop == '1400':
        viljanimi = 'Kaura'
    elif crop == '1110':
        viljanimi = 'Syysvehnä'
    elif crop == '1120':
        viljanimi = 'Kevätvehnä'
    elif crop == '1230':
        viljanimi = 'Ruis'
    else:
        viljanimi = 'None'
            
    plt.rcParams['text.usetex'] = False
    
    # define min and max values and colormap for the plots
    value_min = -40
    value_max = 40
    cmap = 'RdBu'
    norm = mcolors.TwoSlopeNorm(vmin = value_min, vmax = value_max, vcenter = 0)
    
            
    fig = plt.figure(figsize = (6,10))
    ax_map = fig.add_axes([0, 0, 1, 1])
    dfeuropaFIN.plot(ax = ax_map, color = 'lightgray')#, color=colors) #['#C62828', '#283593', '#283593', '#FF9800'])
    ax_map.set_axis_off()
    
    data.plot(ax = ax_map, column = 'deviation', marker = 's', markersize = 25, # marker = 'o' for bullet
                       vmin = value_min, vmax = value_max, cmap = cmap, norm = norm, edgecolor = None)

    ax_map.axis('off')
    #ax_map.set(title = pvm)
    #print(str(round(nationalPred)), deviationNational)
    ax_map.annotate('Koko maan satoennuste:\n\n' + str(round(nationalPred)) + ' kg/ha (' + deviationNationaltxt + '%)',
        xy=(596327, 6823806),  xycoords='data', weight='bold',
    xytext=(0.35, 0.55), textcoords='axes fraction', # xytext=(0.95, 0.55)
    #arrowprops=dict(facecolor='black', shrink=0.05),
    horizontalalignment='right', verticalalignment='top',
    )

    ax_map.annotate('Harmaat alueet: ei ennustetta (liikaa epävarmuutta/ei viljelyä).',
        xy=(696327, 6603806),  xycoords='data',
    xytext=(1.2, 0.05), textcoords='axes fraction', # xytext=(0.95, 0.55)
    #arrowprops=dict(facecolor='black', shrink=0.05),
    horizontalalignment='right', verticalalignment='top',
    )    
    
    
    # define a mappable based on which the colorbar will be drawn
    mappable = cm.ScalarMappable(
        norm = mcolors.TwoSlopeNorm(vmin = value_min, vmax = value_max, vcenter = 0),
        cmap = cmap
    )
    # Luke-logo:
    #arr_img = plt.imread('/projappl/project_2009889/metadata/Luke-logo-web.png', format = 'png')
    arr_img = plt.imread('/projappl/project_2009889/metadata/Luonnonvarakeskus_LOGO_COL-cropped.png', format = 'png')

    imagebox = OffsetImage(arr_img, zoom = 0.05) # 0.08
    #Container for the imagebox referring to a specific position *xy*.
    ab = AnnotationBbox(imagebox, (42327, 6653806), frameon = False) #(42327, 6853806)
    ax_map.add_artist(ab)

    # define position and extent of colorbar
    #cb_ax = fig.add_axes([0.1, 0.1, 0.8, 0.05]) # horizontal
    cb_ax = fig.add_axes([1, .1, 0.025, 0.85])

    #ax_map.set_title('Satoennuste ' + viljanimi + ' (' + pvm + ')')
    #Kaura, hehtaarisatoennuste keskimääräisestä (%), tilanne 15.7.2024
    ax_map.set_title(viljanimi + ', hehtaarisatoennuste keskimääräisestä (%), tilanne ' +  pvm, fontsize = 14, weight='bold')
    # draw colorbar
    cbar = fig.colorbar(mappable, cax = cb_ax, orientation='vertical', label =  'Satoennuste verrattuna 8 vuoden alueelliseen keskisatoon (%)')
    #cbar.ax.tick_params(labelsize = 16) # ei toimi
    
    # Logo:
    # cb_ax.add_artist(ab)
    
    if region == 'gridded':
        fp = os.path.join(imagepath, 'Satoennuste-' + crop + '-' + pvm00 + '-10kmruutu.png')
    else:
        fp = os.path.join(imagepath, 'Satoennuste-' + crop + '-' + pvm00 + '.png')

    plt.savefig(fp, dpi=300, bbox_inches='tight')
    print(f"Saving image in {fp}")
    
    return fp





# MAIN:
def main(args):
    try:
        if not args.inputpath or not args.region:
            raise Exception('Missing input filepath or crop type argument. Try --help .')

        print(f'\n20-make-maps-Finnish.py')    
        
        s3_resource = boto3.resource('s3', endpoint_url='https://a3s.fi')
        
        imagepath = Path(os.path.expanduser(args.inputpath) + 'img', args.region)
        imagepath.mkdir(parents=True, exist_ok=True)
                
        # Map of Europe, take Finland:
        dfeuropa = gpd.read_file(fpeuropa)
        dfeuropaFIN = dfeuropa[(dfeuropa['TZID'] == 'Europe/Helsinki') | (dfeuropa['TZID'] == 'Europe/Mariehamn')].to_crs('epsg:3067')           
        
        # Read national predictions:
        nationalPreds = readNationalYields(args.inputpath)
        year = nationalPreds['Year'][0][:-1]
        
        # Date:
        pvm0 = args.inputpath
        pvm00 = pvm0.split('/')[-2]
        # Translate to Finnish:
        pvm000 = datetime.date.fromisoformat(pvm00)
        pvm = pvm000.strftime("%d.%m.%Y")
        #pvm = pvm000.strftime("%d %B %Y")

        
        # For each crop:
        for crop in nationalPreds['Crop'].to_list():
            if not crop in [1110, 1120, 1310, 1320, 1400]:
                continue # only these crops have reference data (long term means)
                
            #print(crop)
            # Area filter:
            if crop == 1310:
                filtteri = 1100 # ha
            else:
                filtteri = 100 # ha


            #print(nationalPreds[nationalPreds['Crop'] == crop]['Yield'])
            # National pred:
            nationalPred = nationalPreds[nationalPreds['Crop'] == crop]['Yield'].values[0]
            
            # Read long-term mean yields, national:   
            longTermNationalYield = readLongtermNationalYields(str(crop))
            
            if longTermNationalYield:
            
                # Read long term yields:
                fpregion = '/projappl/project_2009889/metadata/' + args.region + 'Yields/longTermYields/Yields-' + str(crop) + '.csv'
                longTermRegionalYield = pd.read_csv(fpregion)


                if args.region == 'maakunta':   
                    
                    # We have long term regional yields:
                    longTermRegionalYield2 = longTermRegionalYield.set_index('NATCODE')

                    # Read preds:
                    fp = os.path.join(args.inputpath, str(crop) + '-' + year, str(crop) + '-maakunnittain.csv')
                    dfPreds0 = pd.read_csv(fp)
                    print(f'Filtering out maakunnat having less than {filtteri} ha of predicted cropland...')
                    dfPreds = dfPreds0[dfPreds0['Area'] > filtteri]
                    
                    if crop == 1320:
                        # Halutaan peittää 21 Ahvenanmaa, 19 Lappi, 18 Kainuu, 17 P-Pmaa, 16 Keski-pmaa, 12 P-Karjala
                        dfPreds = dfPreds[~dfPreds['Maakunta'].isin([21, 19, 18, 17, 16, 12])]
                    
                    dfPreds.rename(columns = {'weighted_yield': 'preds', 'Area': 'predArea'}, inplace = True)
                    dfPreds2 = dfPreds.set_index('Maakunta')   
                    
                    # Kartta:
                    fp = "/projappl/project_2009889/metadata/hallintorajat/maakunnat_2020_milj.shp"

                    gdfmaakunta = gpd.read_file(fp)
                    gdfmaakunta['Maakunta'] = gdfmaakunta['NATCODE'].astype('int')
                    regionborders = gdfmaakunta.set_index('Maakunta')
                                        
                    # Make deviation data from preds and long term yields:
                    data = pd.concat([dfPreds2, longTermRegionalYield2], axis = 1) # pitäisi olla ok; concat toimii, kun index integer
                    #print(data.head(20))
                    data['deviation'] = round(((data['preds'] - data['weighted_yield']) / data['weighted_yield']) * 100, 0)

                    gdfdata = pd.concat([regionborders, data], axis = 1)


                elif args.region == 'kunta':
                    print('Kunta yields not done yet... TODO!')
                    fp = "/Users/myliheik/Documents/GISdata/mml/hallintorajat_milj_tk/Hallintorajat2020-teemakartoille-ei-merialueita/kunnat_2020_milj.shp"
                    
                    
                    
                   
                else:
                    print('\n---- Region is grid! -----\n')
                    # Read long term grid yields:
                    
                    
                    
                    
                    filename = os.path.join(args.inputpath, str(crop) + '-2024', 'TCNPreds.pkl')

                    # Read preds:
                    basedir = Path(filename).parents[3]
                    setti = utils._parse_setti_from_predsPath(filename)
                    print(setti)

                    cropid = setti.split('-')[:-1][0]
                    year = setti.split('-')[-1]

                    if setti == '1300-' + year:
                        setti = '1310-1320-' + year

                    parcelfile = os.path.join(basedir, 'dataStack', 'parcelID_' + setti + '.pkl')
                    parcels = pd.DataFrame(utils._load_intensities(parcelfile))
                    parcels[['Year', 'parcelID0', 'Croptype', 'Maakunta', 'Municipality', 'Area']] = parcels[0].str.split('_', expand = True) # '2024_16277895_1320_2_529_141'
                    parcels.rename(columns = {0: 'parcelID'}, inplace = True)

                    array = utils._load_intensities(filename)
                    df0 = pd.DataFrame(array.squeeze())
                    df = df0.iloc[ :, -1:] # last prediction only
                    df.columns = ['Prediction']
                    
                    if not df.shape[0] == parcels.shape[0]:
                        print('somethings wrong!')
                    # Merge preds and parcels:                        
                    dfall = pd.concat([parcels, df], axis = 1)
                    
                    # merge with metafile:
                    metadf = pd.read_csv(metafilefp)
                    
                    dfall2 = dfall.merge(metadf, how = 'inner')
                    
                    # Weighted mean:
                    #dfall2['Area'] = dfall2['Area'].astype(float)
                    # for weighted mean:
                    #dfall2['tmp_weighted_yield'] = dfall2['Yield'] * dfall2['Area']
                                                           
                    #dfall3 = dfall2[['10kmCELLCODE', 'tmp_weighted_yield', 'Area']].groupby('10kmCELLCODE').agg('sum')
                    #dfall3['weighted_yield'] = dfall3['tmp_weighted_yield'] / dfall3['Area']
                    

                    # include grid that have > 5 parcels: 
                    print(f'Filtering out grids having less than 6 of predicted parcels...')
                    dfall2['count'] = dfall2[['10kmCELLCODE', 'EOFORIGIN10km', 'NOFORIGIN10km', 'parcelID']].groupby(['10kmCELLCODE', 'EOFORIGIN10km', 'NOFORIGIN10km'])['parcelID'].transform("count")
                    dfall22 = dfall2[dfall2['count'] > 5]
                    # take mean of the 10km grid:
                    dfall3 = dfall22.groupby(['10kmCELLCODE', 'EOFORIGIN10km', 'NOFORIGIN10km']).mean().reset_index()

                    # make geopandas:
                    gdf = gpd.GeoDataFrame(dfall3[['10kmCELLCODE', 'EOFORIGIN10km', 'NOFORIGIN10km', 'Prediction']], 
                                           geometry = gpd.points_from_xy(dfall3['EOFORIGIN10km'], dfall3['NOFORIGIN10km']),
                                              crs = dfeuropaFIN.crs)
                    gdfdata = gdf.merge(longTermRegionalYield, on = '10kmCELLCODE')
                    print(f'{round((((len(gdfdata) - len(gdf))/ len(gdf))+1)*100, 0)}% ruuduista löytyi pitkänajan keskisatotieto.')
                    
                    gdfdata['deviation'] = round(((gdfdata['Prediction'] - gdfdata['yield']) / gdfdata['yield']) * 100, 0)

                
                
                # Save all data for backup:
                #lista = []
                #lista.append(longTermNationalYield)
                #lista.append(nationalPred)
                #lista.append(gdfdata)
                #lista.append(crop)
                #lista.append(imagepath)
                #lista.append(dfeuropaFIN)
                #lista.append(pvm)
                #lista.append(pvm00)
                #print(lista)
                #fptmp = os.path.join('/scratch/project_2009889/temp2', str(crop) + '.pkl')
                #print(f'Saving data into {fptmp}')
                #utils.save_intensities(fptmp, lista)
                
                fp = plotMaps(longTermNationalYield, nationalPred, gdfdata, str(crop), imagepath, dfeuropaFIN, pvm, pvm00, args.region)
                
                # boto3:               
                if args.region == 'gridded':
                    boto3file = 'Satoennuste-' + str(crop) + '-10kmruutu.png'
                    print(f'Saving images into Allas {boto3file}')
                    s3_resource.Object(my_bucketname, boto3file).upload_file(fp, ExtraArgs={'ACL':'public-read'})
                    # Saving also with date:
                    boto3file = 'Satoennuste-' + str(crop) + '-' + pvm00 + '-10kmruutu.png'
                    s3_resource.Object(my_bucketname, boto3file).upload_file(fp, ExtraArgs={'ACL':'public-read'})               
                else:
                    boto3file = 'Satoennuste-' + str(crop) + '.png'
                    print(f'Saving images into Allas {boto3file}')
                    s3_resource.Object(my_bucketname, boto3file).upload_file(fp, ExtraArgs={'ACL':'public-read'})
                    # Saving also with date:
                    boto3file = 'Satoennuste-' + str(crop) + '-' + pvm00 + '.png'
                    s3_resource.Object(my_bucketname, boto3file).upload_file(fp, ExtraArgs={'ACL':'public-read'})

        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write output. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputpath',
                        help='Filepath of yield predictions.',
                        type=str)  
    parser.add_argument('-r', '--region',
                         type=str, default='maakunta',
                         help='Region. E.g. maakunta, kunta, or gridded. Default: maakunta.')    
    #parser.add_argument('-d', '--doy', action='store', dest='doys',
    #                   type=str, nargs='*', default=['139', '169', '200'],
    #                   help="Optionally e.g. -d 139 169 200, default all") 

    args = parser.parse_args()
    main(args)
