"""

"""

"""
@author: MY

For creating forecasting sets from IACS parcel data (kasvulohkodata)

2024-06-18
2024-06-27 added grid cell ID by parcel centroid.

Filterit: 

1) Filter out broken typologies -> None

2) Filteröidään pois lohkot alle FILTERED_OUT eli oletuksena 1ha.

3) Kaikkien saatavilla olevien vuosien otantojen satotilat mukaan (optional)


SELECT klilm_tunnus, vuosi, maatila_tunnus, plvuosi_peruslohkotunnus, kasvulohkotunnus, 
kvi_kasvikoodi, kle_lajikekoodi, luomuvkd_koodi, pintaala, onkoekologinenala, 
geoloc as GEOM 
FROM GISKASITTELYMGR.gka_kasvulohkogeometria 
WHERE VUOSI = '2024'

***

After this run: 01-splitshp-shadow.py etc.

By default for these crops: ['1110', '1120', '1230', '1310', '1320', '1400', '2100', '2200', '3100', '4100', '4200']

In 2024 for only these reported: ['1120', '1300', '1400']

RUN:

# For all parcels, default crops:
python 00-preprecessing-forecasting.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2024/klohkot2024-062024.gpkg \
-o /Users/myliheik/Documents/GISdata/satotutkimus/forecasting-2024/ -g 1

# Selected parcels, from sato-otanta:
python 00-preprecessing-forecasting.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2024/klohkot2024-062024.gpkg \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-o /Users/myliheik/Documents/GISdata/satotutkimus/forecasting-2024/ -g 1





"""
import pandas as pd
import geopandas as gpd
import numpy as np
import os.path
from pathlib import Path
import argparse
import textwrap
import math

import warnings
warnings.filterwarnings("ignore")

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def readLPIS(fpkasvu, dataSato, setti, FILTERED_OUT):
    kasvulohko = gpd.read_file(fpkasvu)
    kasvulohko.rename(columns={"KVI_KASVIKOODI": "KASVIKOODI", "KVI_KASVIK": "KASVIKOODI", "MAATILA_TUNNUS": "MAATILA_TU", "KLILM_TUNN": "KLILM_TUNNUS"
                              }, inplace=True)

    year = str(kasvulohko['VUOSI'][0])
    projection = kasvulohko.crs
    
    print(f'The total number of parcels: {len(kasvulohko)}')
    
    kasvulohko00 = kasvulohko[~kasvulohko.geometry.isna()].copy()
    kasvulohko0 = kasvulohko00[~kasvulohko00['KASVIKOODI'].isna()]
    
    if len(kasvulohko) - len(kasvulohko00) > 0:
        print(f'There were {len(kasvulohko) - len(kasvulohko00)} nas in parcel geometries! Excluded now.')
        
    kasvulohko0['P_ALA_HA'] = round(kasvulohko0.area/10000, 2)
 
    print(f'The mean area of parcels: {kasvulohko0["P_ALA_HA"].mean()}')

    # Combine all potatoes: (potato is potato)    
    mask = kasvulohko0['KASVIKOODI'].str.startswith('31')
    kasvulohko0['KASVIKOODI'][mask] = '3100'
    # Combine winter and spring oilseed rape (rapsi), because yield data combined:
    mask = kasvulohko0['KASVIKOODI'] == '4220'
    kasvulohko0['KASVIKOODI'][mask] = '4200'
    mask = kasvulohko0['KASVIKOODI'] == '4210'
    kasvulohko0['KASVIKOODI'][mask] = '4200'
    # Combine all turnip rape (rypsi):
    mask = kasvulohko0['KASVIKOODI'] == '4120'
    kasvulohko0['KASVIKOODI'][mask] = '4100'
    mask = kasvulohko0['KASVIKOODI'] == '4110'
    kasvulohko0['KASVIKOODI'][mask] = '4100'    
    # Combine all pea (feed and food):
    mask = kasvulohko0['KASVIKOODI'] == '2110'
    kasvulohko0['KASVIKOODI'][mask] = '2100'
    mask = kasvulohko0['KASVIKOODI'] == '2120'
    kasvulohko0['KASVIKOODI'][mask] = '2100'
    
    row_mask = kasvulohko0.KASVIKOODI.isin(setti)
    filtered0 = kasvulohko0[row_mask]
    
    #Filter out parcels < FILTERED_OUT
    filtered1 = filtered0[filtered0["P_ALA_HA"] > FILTERED_OUT].copy()

    print(f'LPIS was filtered by area (< {FILTERED_OUT} ha) and crop types ({", ".join(setti)}). {len(filtered1)} parcels remains.')
    
    # Crop farms:
    filtered1.MAATILA_TU = filtered1.MAATILA_TU.astype('int').copy()
    if dataSato:
        print('Parcels from satotilat (included in sato-otanta some time between 2016-2023) included.')
        df = pd.read_csv(dataSato)
        tilanumerot = df['MTYRI_TILTU'].drop_duplicates()
        print(f'Parcels from {len(tiltut)} otantatilaa included only.')
        row_mask = filtered1.MAATILA_TU.isin(tilanumerot)
        filtered2 = filtered1[row_mask].copy()
        #len(filtered2)
    else:
        print('All parcels included (if not filtered by size)')
        filtered2 = filtered1

    # drop broken typologies:
    row_mask2 = filtered2.geometry.is_valid
    filtered3 = filtered2[row_mask2]

    filtered3 = filtered3.rename(columns={'MAATILA_TU': 'farm_ID', 'KASVIKOODI': 'plant_ID'}).copy()
    print(f'Broken typologies were checked. {len(filtered3)} parcels remains.')
    

    tmpnrkaikki = filtered0[['KLILM_TUNNUS', 'KASVIKOODI']].groupby(['KASVIKOODI']).count()
    tmpnr = filtered3[['KLILM_TUNNUS', 'plant_ID']].groupby(['plant_ID']).count()
    tmpala = round(filtered3[['P_ALA_HA', 'plant_ID']].groupby(['plant_ID']).sum()/filtered0['P_ALA_HA'].sum(), 2)
    alatotos = round(filtered3[['P_ALA_HA', 'plant_ID']].groupby(['plant_ID']).sum(), 0)
    alatiacs = round(filtered0[['P_ALA_HA', 'KASVIKOODI']].groupby(['KASVIKOODI']).sum(), 0)
    
    print('\n--------')
    print(f"The share of crop types in the data, by area and by number: \n{pd.concat([tmpala, tmpnr, alatotos, tmpnrkaikki, alatiacs], axis = 1)}")
    
    return filtered3, year, projection


def addAdministrativeAreaCode(gdf, year, projection, out_dir_path, setti): 
    
    # Read regionpath:
    # haetaan kasvulohkolle kunta:
    # luetaan kuntarajat
    fp = "/Users/myliheik/Documents/GISdata/mml/hallintorajat_milj_tk/Hallintorajat2020-teemakartoille-ei-merialueita/kunnat_2020_milj.shp"
    gdfkunta = gpd.read_file(fp)
    gdfkunta['KUNTA_KNRO_VUOSI'] = gdfkunta['NATCODE'].astype('int')
    
    # haetaan satolohkoille kuntatieto:
    satolohkolleKunta = gpd.overlay(gdf, gdfkunta, how='intersection')
    
    # luetaan maakuntarajat
    fp = "/Users/myliheik/Documents/GISdata/mml/hallintorajat_milj_tk/Hallintorajat2020-teemakartoille-ei-merialueita/maakunnat_2020_milj.shp"
    gdfmaakunta = gpd.read_file(fp)
    gdfmaakunta['MAAKUNTA_KNRO_VUOSI'] = gdfmaakunta['NATCODE'].astype('int')
    
    # haetaan satolohkoille maakuntatieto:
    gdf2 = gpd.overlay(satolohkolleKunta, gdfmaakunta, how='intersection')   

    gdf2['parcelID'] = gdf2['KLILM_TUNNUS'].apply(lambda x: "{}{}{}".format(year,'_', x)) + '_' + gdf2['plant_ID'].astype(str) + '_' + gdf2['MAAKUNTA_KNRO_VUOSI'].astype(str) + '_' + gdf2['KUNTA_KNRO_VUOSI'].astype(str) + '_' + gdf2['PINTAALA'].astype(str)
    gdf2.crs = projection
    print(f'Municipality and maakunta added to parcelID.') 
    
    
    print(f'\nThe share of parcels per Maakunta:')
    tmp = gdf2[['KLILM_TUNNUS', 'plant_ID', 'MAAKUNTA_KNRO_VUOSI']].groupby(['plant_ID', 'MAAKUNTA_KNRO_VUOSI']).count().reset_index()
    print(tmp)
    if setti == ['1110', '1120', '1230', '1310', '1320', '1400', '2100', '2200', '3100', '4100', '4200']:
        # all, no need to print out:
        # Save metadata into:
        outputfile3 = os.path.join(out_dir_path, 'metafileshares-' + str(year) + '.csv')  
    else:    
        # Save metadata into:
        outputfile3 = os.path.join(out_dir_path, 'metafileshares-' + str(year) + '-' + '-'.join(setti) + '.csv')  
        
    print(f'\nSaving the share of parcels per Maakunta into {outputfile3}')
    tmp.to_csv(outputfile3, index = False)
    print('\n--------\n')    
    
    ######## get grid cell ID by centroid:
    gdf2['keskipiste'] = gdf2.centroid
    gdf2['lon'] = gdf2.keskipiste.x
    gdf2['lat'] = gdf2.keskipiste.y
        
    # Calculate 10km grid coords:
    for index, row in gdf2[['lon', 'lat']].iterrows():
        x = round_down(row['lon'], -4)
        y = round_down(row['lat'], -4)
        gdf2.loc[index, 'EOFORIGIN10km'] = x
        gdf2.loc[index, 'NOFORIGIN10km'] = y

        #x = round_down(row['lon'], -3)
        #y = round_down(row['lat'], -3)
        #gdf2.loc[index, 'EOFORIGIN1km'] = x
        #gdf2.loc[index, 'NOFORIGIN1km'] = y

        #x = round(row['lon']/5000) * 5000
        #y = round(row['lat']/5000) * 5000
        #gdf2.loc[index, 'EOFORIGIN5km'] = x
        #gdf2.loc[index, 'NOFORIGIN5km'] = y    
    
    #gdf2['5kmCELLCODE'] = "5kmN" + (gdf2["NOFORIGIN5km"]/1000).astype(int).map(lambda x: f'{x:0>4}') + "E" (gdf2['EOFORIGIN5km']/1000).astype(int).map(lambda x: f'{x:0>4}')
    #gdf2['1kmCELLCODE'] = "1kmN" + (gdf2["NOFORIGIN1km"]/1000).astype(int).map(lambda x: f'{x:0>4}') + "E" + (gdf2['EOFORIGIN1km']/1000).astype(int).map(lambda x: f'{x:0>4}')   
    gdf2['10kmCELLCODE'] = "10kmN" + (gdf2["NOFORIGIN10km"]/1000).astype(int).map(lambda x: f'{x:0>4}') + "E" + (gdf2['EOFORIGIN10km']/1000).astype(int).map(lambda x: f'{x:0>4}')

    ######## end of grid stuff.
    
    if setti == ['1110', '1120', '1230', '1310', '1320', '1400', '2100', '2200', '3100', '4100', '4200']:
        # all, no need to print out:
        # Save metadata into:
        outputfile = os.path.join(out_dir_path, 'metafile-' + str(year) + '.csv')  
    else:    
        # Save metadata into:
        outputfile = os.path.join(out_dir_path, 'metafile-' + str(year) + '-' + '-'.join(setti) + '.csv')  
        
    print(f'\nSaving metadata into {outputfile}')
    gdf2[['parcelID', 'PINTAALA', 'ONKOEKOLOGINENALA', 'KUNTA_KNRO_VUOSI', 'NAMEFIN_1', 'MAAKUNTA_KNRO_VUOSI', 'NAMEFIN_2', '10kmCELLCODE', 'NOFORIGIN10km', 'EOFORIGIN10km']].to_csv(outputfile, index = False)
          
    #print(gdf2.head())
    return gdf2.reset_index()
          
        
def savingParcels(kasvulohkot, out_dir_path, year, setti):
    
    if setti == ['1110', '1120', '1230', '1310', '1320', '1400', '2100', '2200', '3100', '4100', '4200']:
        # all, no need to print out:
        outputfile2 = os.path.join(out_dir_path, 'parcels-' + str(year) + '.shp')  
    else:    
        outputfile2 = os.path.join(out_dir_path, 'parcels-' + str(year) + '-' + '-'.join(setti) + '.shp')  
        
    print(f'Saving geometries to {outputfile2}')           
    kasvulohkot[['parcelID', 'geometry']].to_file(driver = 'ESRI Shapefile', filename = outputfile2)

    print('ParcelID is in format: YEAR_parcelID_CROPTYPE_MAAKUNTA_KUNTA_AREA. Area is in acres.')

  
    
# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputpath:
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n00-preprecessing-forecasting.py')        
        print(f'\nLPIS data in: {args.inputpath}')
        
        # directory for output:
        out_dir_path = args.outputshppath
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)
        
        print(f'Selected crops: {", ".join(args.setti)}')

        # READ LPIS, filter out too small parcels and select only relevant crop types:
        kasvulohkot, year, projection = readLPIS(args.inputpath, args.referencepath, args.setti, args.filter)
        print(kasvulohkot.head())
        
        kasvulohkot2 = addAdministrativeAreaCode(kasvulohkot, year, projection, out_dir_path, args.setti)  
        print(kasvulohkot2.head())

        # Saving:  
        savingParcels(kasvulohkot2, out_dir_path,year, args.setti)
                     
        
        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write out. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))
    parser.add_argument('-f', '--setti', action='store', dest='setti',
                         type=str, nargs='*', default = ['1110', '1120', '1230', '1310', '1320', '1400', '2100', '2200', '3100', '4100', '4200'],
                         help='List of datasets. Can be multiple. E.g. -f 1310 1320.')
    parser.add_argument('-g', '--filter',
                        help='Filter out parcels < threshold.',
                        default = 1,
                        type=float)   
    parser.add_argument('-i', '--inputpath',
                        help='Parcel geometries (LPIS)',
                        type=str)  
    parser.add_argument('-j', '--referencepath',
                        help='Filepath to farm ids to be included in the sample.',
                        type=str)  
    parser.add_argument('-o', '--outputshppath',
                        help='Directory to save parcel geometries.',
                        type=str)  
    parser.add_argument('--debug',
                        help='Verbose output for debugging.',
                        action='store_true')

    args = parser.parse_args()
    main(args)






    
