"""
2024-05-14 

@author: MY

For creating training sets from annual yield data. From Pinja's data:

stat_sato on skeema, lukedb2prod.ns.luke.fi tietokannan osoite.

select sv.tilatunnus, sv.kasitekoodi1, sk.kod_selite_fi1, sv.kasitekoodi2, sk.kod_selite_fi2, sv.kasitekoodi3, sk.kod_selite_fi3, sv.numeroarvo from stat_sato.sato_v sv left join stat_sato.sato_koodit sk on sv.kasitekoodi1 = kasitekoodi1 and sv.kasitekoodi2 = sk.kod_kasitekoodi2 and sv.kasitekoodi3 = sk.kod_kasitekoodi3 where sv.vuosi = 2022 and sv.kasitekoodi2 in ('14545', '20941') and kasitekoodi3 in ('61197', '386579', '387139', '387019', '387023', '61223');

# Testattu vain v. 2023 herneellä, joka puuttui tällä hetkellä.


Herne, härkäpapu, peruna ja muut kaikki samassa

Filterit: 
1) yhden viljalajin pellot < 30km etäisyydellä

2) filter out broken typologies -> None

3) Filteröidään pois lohkot alle FILTERED_OUT eli oletuksena 1ha.

4) filteröidään pois ne joilla kylvetyn ja korjatun erotus > 0.2 tai < -0.2 eli 20%:n satomenetys (ei tässä versiossa, koska 
muuttuja viljelyala puuttuu. sato == korjattu_ala, viljelyala == kylvetty_ala

PUUTTUU myös kuntatieto!!!


***

After this run: splitshp-shadow.py etc.

By default for these crops: ['1110', '1120', '1230', '1310', '1320', '1400', '2100', '2200', '3100', '4100', '4200']

RUN:

# For all crops, FILTERED_OUT = 0.5ha:
python 00-preprecessing-training-set-with-Pinja-data.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2023/Kasvulohkot2023.gpkg \
-j /Users/myliheik/Documents/myCROPYIELD/data/viljelijakysely/Pinjalta_select_sv_vuosi_sv_tilatunnus_sv_kasitekoodi1_sk_kod_selite_fi1_2023.csv \
-y 2023 \
-o /Users/myliheik/Documents/myCROPYIELD/data/training-2023/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 2100

# Selected crops: (if needed) / jos olisi tarve 2022:
python 00-preprecessing-training-set-with-Pinja-data.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2022/kasvulohkot2022-mod.shp \
-j /Users/myliheik/Documents/myCROPYIELD/data/viljelijakysely/Pinjalta_select_sv_vuosi_sv_tilatunnus_sv_kasitekoodi1_sk_kod_selite_fi_2022.csv \
-y 2018 \
-o /Users/myliheik/Documents/myCROPYIELD/data/training-2022/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 4100 


"""
import pandas as pd
import geopandas as gpd
import numpy as np
import os.path
from pathlib import Path
import argparse
import textwrap

import warnings
warnings.filterwarnings("ignore")



def readLPIS(fpkasvu, dataSato, setti, year, FILTERED_OUT):
    kasvulohko = gpd.read_file(fpkasvu)
    kasvulohko.rename(columns={"KVI_KASVIKOODI": "KASVIKOODI", "KVI_KASVIK": "KASVIKOODI", "MAATILA_TUNNUS": "MAATILA_TU", "KLILM_TUNN": "KLILM_TUNNUS"}, inplace=True)
    print(kasvulohko.columns)
    
    kasvulohko00 = kasvulohko[~kasvulohko.geometry.isna()].copy()
    kasvulohko0 = kasvulohko00[~kasvulohko00['KASVIKOODI'].isna()]
    
    if len(kasvulohko) - len(kasvulohko00) > 0:
        print(f'There were {len(kasvulohko) - len(kasvulohko00)} nas in parcel geometries! Excluded now.')
        
    kasvulohko0['P_ALA_HA'] = kasvulohko0.area/10000
    print(f'The mean area of parcels in {year}: {kasvulohko0["P_ALA_HA"].mean()}')
        
    tilanumerot = dataSato['tiltu']
    #Filter out parcels < FILTERED_OUT
    kasvulohko2 = kasvulohko0[kasvulohko0["P_ALA_HA"] > FILTERED_OUT].copy()

    # Combine all potatoes: (potato is potato)    
    mask = kasvulohko2['KASVIKOODI'].str.startswith('31')
    kasvulohko2['KASVIKOODI'][mask] = '3100'
    # Combine winter and spring oilseed rape (rapsi), because yield data combined:
    mask = kasvulohko2['KASVIKOODI'] == '4220'
    kasvulohko2['KASVIKOODI'][mask] = '4200'
    mask = kasvulohko2['KASVIKOODI'] == '4210'
    kasvulohko2['KASVIKOODI'][mask] = '4200'
    # Combine all turnip rape (rypsi):
    mask = kasvulohko2['KASVIKOODI'] == '4120'
    kasvulohko2['KASVIKOODI'][mask] = '4100'
    mask = kasvulohko2['KASVIKOODI'] == '4110'
    kasvulohko2['KASVIKOODI'][mask] = '4100'    
    # Combine all pea (feed and food):
    mask = kasvulohko2['KASVIKOODI'] == '2110'
    kasvulohko2['KASVIKOODI'][mask] = '2100'
    mask = kasvulohko2['KASVIKOODI'] == '2120'
    kasvulohko2['KASVIKOODI'][mask] = '2100'
    
    
    if setti is None:
        # All crops:
        satokyselykasvit = ['1110', '1120', '1230', '1310', '1320', '1400', '2100', '2200', '3100', '4100', '4200']
    else:
        satokyselykasvit = setti

    row_mask = kasvulohko2.KASVIKOODI.isin(satokyselykasvit)
    filtered1 = kasvulohko2[row_mask]
    print(f'LPIS was filtered by area (< {FILTERED_OUT} ha) and crop types {satokyselykasvit}. {len(filtered1)} parcels remains.')
    
    # Crop farms:
    filtered1.MAATILA_TU = filtered1.MAATILA_TU.astype('int').copy()
    row_mask = filtered1.MAATILA_TU.isin(tilanumerot)
    filtered2 = filtered1[row_mask].copy()
    len(filtered2)

    # drop broken typologies:
    row_mask2 = filtered2.geometry.is_valid
    filtered3 = filtered2[row_mask2]

    filtered3 = filtered3.rename(columns={'MAATILA_TU': 'farm_ID', 'KASVIKOODI': 'plant_ID'}).copy()
    print(f'Parcels were filtered by survey farms. Broken typologies were checked. {len(filtered3)} parcels remains.')
    
    filtered3['farmID'] = filtered3['farm_ID'].apply(lambda x: "{}{}{}".format(year,'_', x)) + '_' + filtered3['plant_ID'].astype(str)
    #filtered3['farmID2'] = filtered3['KLILM_TUNNUS'].apply(lambda x: "{}{}{}".format(year,'_', x)) + '_' + filtered3['plant_ID'].astype(str)

    tmpnr = filtered3[['KLILM_TUNNUS', 'plant_ID']].groupby(['plant_ID']).count()
    tmpala = round(filtered3[['P_ALA_HA', 'plant_ID']].groupby(['plant_ID']).sum()/filtered3['P_ALA_HA'].sum(), 2)
    
    print(f"The share of crop types in the data: \n{pd.concat([tmpala, tmpnr], axis = 1)}")
    
    return filtered3

def readRefe(referencepath, year):
    # Read reference file:
    dataSato0 = pd.read_csv(referencepath, sep = ',')
    dataSato = dataSato0[dataSato0.vuosi == year]
    dataSato.rename(columns={"tilatunnus": "tiltu"}, inplace = True)
    return dataSato

    
def munchCropYield(setti, dataSato, year):

    crops = {
      "1110": ["syysvehna"],
      "1120": ["kevatvehna"],
      "1230": ["ruis"],
      "1310": ["rehuohra"],
      "1320": ["mallasohra"],
      "1400": ["kaura"],
      "2200": ["harkapapu"],
      #"2100": "herne",
      "2100": ["ruokaherne", "rehuherne"],
      "2110": ["ruokaherne"],
      "2120": ["rehuherne"],
      #"3100": "peruna",
      "3100": ["ruokaperuna", "ruokateolperuna", "tarkkelysperuna", "varhaisperuna"],
      "3110": ["ruokaperuna"],
      "3120": ["ruokateolperuna"],
      "3130": ["tarkkelysperuna"],
      "3150": ["varhaisperuna"],
      "4100": ["rypsi"],    
      "4200": ["rapsi"],      
    }

    cropids = {
    'syysvehna': '1110',
    'kevatvehna': '1120',
    'ruis': '1230',
    'rehuohra': '1310',
    'mallasohra': '1320',
    'kaura': '1400',
    'harkapapu': '2200',
    'herne': '2100',
    'ruokaherne': '2110',
    'rehuherne': '2120',
    'peruna': '3100',
    'ruokaperuna': '3110',
    'ruokateolperuna': '3120',
    'tarkkelysperuna': '3130',
    'varhaisperuna': '3150',
    'rypsi': '4100',
    'rapsi': '4200'    
    }

    kasitekoodicropid2 = {
    386579: '2120',
    387139: '2110',
    61197: '1230'
    }        
    
    cropidkasitekoodi = { # this is used here
    '2100': [386579, 387139],
    '2120': 386579,
    '2110': 387139,
    '1230': 61197,
    '2200': 61223,
    '4100': [387019, 387023],
    '4110': 387019,
    '4120': 387023,
    }  
    
    # Ettei vaan sekoittaisi int indexeihin?
    # https://stackoverflow.com/questions/20250771/remap-values-in-pandas-column-with-a-dict-preserve-nans
    kasitekoodicropid = { # this is used here
    386579: 2100,
    387139: 2100,
    61197: 1230,
    387019: 4100,
    61223: 2200,
    387023: 4100
    }  

    kasitekoodicropid3 = { # this is used here 
    386579: 2100,
    387139: 2100,
    61197: 1230,
    387019: 4100,
    61223: 2200,
    387023: 4100
    }  
    
    kasitekoodicrop = {
    386579: 'Rehuherne',
    387139: 'Ruokaherne',
    61197: 'Ruis',
    387019: 'Kevätrypsi',
    61223: 'Härkäpapu',
    387023: 'Syysrypsi'
    }  

    cropss = []
    if not setti is None: 
        for crop in setti:
            cropss.extend([cropidkasitekoodi.get(crop)])

        def flat(lista):
            flatList = []
            # Iterate with outer list
            for element in lista:
                if type(element) is list:
                    # Check if type is list than iterate through the sublist
                    for item in element:
                        flatList.append(item)
                else:
                    flatList.append(element)
            return flatList


        cropss = flat(cropss)
        print(cropss)

    else: # all types
        cropss = [386579, 387019, 61197, 61223, 387139, 387023]
        print('We do all crops')
        
    df = dataSato[dataSato['kasitekoodi3'].isin(cropss)]
    #print(df[df.tiltu == 979069092])
    #print(df.dtypes)
    print(f"Number of farms in each group: {df['kasitekoodi3'].value_counts()}")
    print(df[['tiltu', 'kod_selite_fi2', 'kasitekoodi3', 'numeroarvo']])
    
    dfg = df.groupby(['tiltu', 'kasitekoodi3', 'kod_selite_fi2']).numeroarvo.sum().to_frame()
    dfg2 = dfg.unstack().dropna().reset_index()
    dfg2.columns = ['tiltu', 'kasitekoodi3', 'Sato', 'Viljelyala']

    # Filter out if 'Viljelyala' < 0.5ha tai dfg2['Sato'] < 10kg
    
    dfg3 = dfg2[~((dfg2['Sato'] < 10) | (dfg2['Viljelyala'] < 0.5))]
    
    print(f"Removing {len(dfg2) - len(dfg2)} farms where 'Sato' < 10kg OR 'Viljelyala' < 0.5ha." )
    
    dfg3['y'] = dfg3['Sato'] / dfg3['Viljelyala']
    df = dfg3.dropna(subset = ['y'])
    
    
    df['croptype'] = df['kasitekoodi3'].replace(kasitekoodicropid, inplace = False) # map tai replace
    df['farm_ID'] = df.tiltu.astype(int) # Remove leading zeros
    
    ## DANGER! laitoin kunnaksi kaikille 801
    if not 'KUNTA_KNRO_VUOSI' in df.columns:
        print(f'Danger! There is no municipality information in the data. Municipality set to 801.')
        df['KUNTA_KNRO_VUOSI'] = '801'
    

    #for crop in cropss:
        #cropid = kasitekoodicropid.get(crop)
        ## jos on kylvetty ala pajon suurempi kuin korjattu, niin sitten on ongelma:
        #dataSato['erotus' + cropid] = (dataSato[crop + '_kylvo'] - dataSato[crop + '_ala'])/dataSato[crop + '_kylvo']
        #dataSato['y' + cropid] = dataSato[crop + '_sato'] / (dataSato[crop + '_ala'] /100)
        # filteröidään pois ne joilla erotus > 0.2 tai < -0.2 eli 20%:n satomenetys:
        #dataSato = dataSato[~(abs(dataSato['erotus' + cropid]) > 0.2)].copy()
        #print(len(dataSato['y' + cropid][~dataSato['y' + cropid].isna()]))
       

    #print(f"\nParcels per crop type: \n {setti} {crop} {year} {len(df)}")

    # Combine all potatoes: (potato is potato)    
    mask = (df['croptype'] > 3100) & (df['croptype'] < 3190)
    df['croptype'][mask] = 3100
    # Combine winter and spring oilseed rape (rapsi), because yield data combined:
    mask = df['croptype'] == 4220
    df['croptype'][mask] = 4200
    mask = df['croptype'] == 4210
    df['croptype'][mask] = 4200
    # Combine all turnip rape (rypsi):
    mask = df['croptype'] == 4120
    df['croptype'][mask] = 4100
    mask = df['croptype'] == 4110
    df['croptype'][mask] = 4100    
    # Combine all pea (feed and food):
    mask = df['croptype'] == 2110
    df['croptype'][mask] = 2100
    mask = df['croptype'] == 2120
    df['croptype'][mask] = 2100    
    
    df3 = df[['tiltu', 'farm_ID', 'y', 'croptype', 'KUNTA_KNRO_VUOSI']].groupby('tiltu', as_index=False, sort=False).agg({'y':'mean', 'farm_ID':'first', 'croptype':'first', 'KUNTA_KNRO_VUOSI':'first'})

    
    df3['farmID'] = str(year) + '_' + df3['farm_ID'].astype(str) + '_' + df3['croptype'].astype(str) 
    df3['farmID2'] = str(year) + '_' + df3['farm_ID'].astype(str) + '_' + df3['croptype'].astype(str) + '_' + df3.y.astype(int).astype(str)
    
    satoy = df3[['tiltu', 'farmID', 'farmID2', 'KUNTA_KNRO_VUOSI', 'croptype', 'y']]
    satoy['y'] = satoy.y.astype(int)
    return satoy.drop(columns = ['tiltu'])

def dataCheckByFarm(gdf):
    
    dataByFarm = gdf[['farmID', 'plant_ID', 'geometry', 'P_ALA_HA']].dissolve(by=['farmID', 'plant_ID'], aggfunc='sum')
    print(f'Number of farms: {len(dataByFarm)}')
    
    # Peltolohkojen keskinäinen etäisyys, lasketaan maksimit. Hyvin karkea laskutapa. Lohkojen ylle sovitetaan suorakulmio, josta lasketaan sivujen pituudet. Maksimietäisyys = max(x) tai max(y).    
    distanceWithin = dataByFarm.geometry.bounds
    distanceWithin['distancex'] = distanceWithin.maxx - distanceWithin.minx
    distanceWithin['distancey'] = distanceWithin.maxy - distanceWithin.miny
    distanceWithin['maxdistance'] = distanceWithin[['distancex', 'distancey']].apply(max, axis=1)
    print('Distance between farms parcels:\n')
    print(distanceWithin['maxdistance'].describe()) # keskim. 4.4km, max 200km
             
    # Discard farms having parcels more apart than 30km:     
    dataByFarm2 = dataByFarm[distanceWithin['maxdistance'] < 30000].copy()
    print(f'Farms having parcels more apart than 30km are discarded. Before {len(dataByFarm)}, after {len(dataByFarm2)} parcels.') 
          
    return dataByFarm2.reset_index()
          
          
def savingParcelsAndReference(dataByFarm, satoy, out_dir_path, satofpout, setti, year):
                    
    if setti is None:
          setti = ['all']
    
    # merge parcels to reference to save AREA:
    satoy2 = satoy.merge(dataByFarm[['farmID', 'P_ALA_HA']], on = 'farmID', how = 'inner')
  
    print(f'How many common farmIDs was found: {len(satoy2)} {len(satoy), len(satoy2)}')
    print(f'The share (%) of farmIDs not found: {(len(satoy) - len(satoy2))/len(satoy)}')
    
    outputfile = os.path.join(satofpout, 'references-' + str(year) + '-' + '-'.join(setti) + '.csv')
    print(f'Saving yields to {outputfile}')
    satoy2[['farmID2', 'KUNTA_KNRO_VUOSI', 'croptype', 'y']].to_csv(outputfile, index = False)
    
    ## Filter out farmIDs that are not for some reason in reference:
    #dataByFarm2 = dataByFarm[dataByFarm['farmID'].isin(satoy['farmID'])]
    dataByFarm2 = dataByFarm.merge(satoy, on = 'farmID', how = 'inner')

    print(f'How many common farmIDs was found: {len(dataByFarm2)} {len(dataByFarm), len(dataByFarm2)}')
    print(f'The share (%) of farmIDs not found: {(len(dataByFarm) - len(dataByFarm2))/len(dataByFarm)}')
    
    outputfile2 = os.path.join(out_dir_path, 'satotilat-' + str(year) + '-' + '-'.join(setti) + '.shp')  
<<<<<<< HEAD
    print(f'Saving geometries to {outputfile2}')      
    
    dataByFarm3 = dataByFarm2[['farmID2', 'geometry']]
=======
    print(f'Saving geometries to {outputfile2}')                                                                                     dataByFarm3 = dataByFarm2[['farmID2', 'geometry']]
>>>>>>> 2d35a37cdd0261da5466d3a2e8b278423eeeef9a
    dataByFarm3.rename(columns = {"farmID2": "farmID"}, inplace = True)
    
    dataByFarm3[['farmID', 'geometry']].to_file(driver = 'ESRI Shapefile', filename = outputfile2)

    # Tallennetaan farmID muotoon VUOSI_farm_CROPTYPE_yield ja referenssitiedostoon: farmID, KUNTA_KNRO_VUOSI, croptype, y

  
    
# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputpath:
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n00-preprecessing-training-set-with-Pinja-data.py')        
        print(f'\nLPIS data in: {args.inputpath}')
        
        # directory for output:
        out_dir_path = args.outputshppath
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)
        
        satofpout = args.satofpout
        Path(satofpout).mkdir(parents=True, exist_ok=True)

        print(args.referencepath)
        dataSato = readRefe(args.referencepath, args.year)

        # READ LPIS, filter out too small parcels and select only relevant crop types:
        kasvulohko = readLPIS(args.inputpath, dataSato, args.setti, args.year, args.filter)
                    
        satoy = munchCropYield(args.setti, dataSato, args.year)
        
        # Discard farms having parcel more apart than 30km:
        dataByFarm = dataCheckByFarm(kasvulohko)

        # Saving:  
        savingParcelsAndReference(dataByFarm, satoy, out_dir_path, satofpout, args.setti, args.year)
                     
        
        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write out. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))
    parser.add_argument('-f', '--setti', action='store', dest='setti',
                         type=str, nargs='*', default = None,
                         help='List of datasets. Can be multiple. E.g. -f 1310 1320.')
    parser.add_argument('-g', '--filter',
                        help='Filter out parcels < threshold.',
                        default = 1,
                        type=float)   
    parser.add_argument('-i', '--inputpath',
                        help='Parcel geometries (LPIS)',
                        type=str)  
    parser.add_argument('-j', '--referencepath',
                        help='Farm-level references',
                        type=str)  
    parser.add_argument('-o', '--outputshppath',
                        help='Selected farm multipolygons out',
                        type=str)  
    parser.add_argument('-s', '--satofpout',
                        help='Farm yields out',
                        type=str)  

    parser.add_argument('-y', '--year',
                        help='Year.',
                        default = 2023,
                        type=int)          
    parser.add_argument('--debug',
                        help='Verbose output for debugging.',
                        action='store_true')

    args = parser.parse_args()
    main(args)






    