"""
@author: MY

For creating training sets from annual yield data.

2024-03-11 Herne, härkäpapu, peruna ja muut kaikki samassa

Filterit: 
1) yhden viljalajin pellot < 30km etäisyydellä

2) filter out broken typologies -> None

3) Filteröidään pois lohkot alle FILTERED_OUT eli oletuksena 1ha.

4) filteröidään pois ne joilla kylvetyn ja korjatun erotus > 0.2 tai < -0.2 eli 20%:n satomenetys:


HUOM! Vuonna 2023 alat oli hehtaareina Mirvan datassa SATO_VUODET_2016_2023_Marialle.csv -> pitäisi olla aina aareina. Koodi huomioi asian.

***

After this run: splitshp-shadow.py etc.

By default for these crops: ['1110', '1120', '1230', '1310', '1320', '1400', '2100', '2200', '3100', '4100', '4200']

RUN:

# For all crops, FILTERED_OUT = 0.5ha:
python 00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2023/Kasvulohkot2023.gpkg \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-y 2023 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2023/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5

# tested on 2022, 2021, 2020, 2019, 2018

# Selected crops: (if needed)
python 00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2018/kasvulohkot2018-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv \
-y 2018 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2018/ \
-s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 2100 2200 3100 4100 4200

# 2022 Mirvan vanhasta datasta kaikki paitsi rypsi ja rapsi:
python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2022/kasvulohkot2022-mod.shp -j /Users/myliheik/Documents/GISdata/satotutkimus/Satotiedot_2022_Marialle.csv-mod -y 2022 -o /Users/myliheik/Documents/GISdata/satotutkimus/training-2022/ -s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f -f 1110 1120 1230 1310 1320 1400 2100 2200 3100

# 2022 puutuva rypsi Pinjalta:
python ../python/00-preprecessing-training-set-with-Pinja-data.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2022/kasvulohkot2022-mod.shp -j /Users/myliheik/Documents/GISdata/satotutkimus/Pinjalta_select_sv_vuosi_sv_tilatunnus_sv_kasitekoodi1_sk_kod_selite_fi1-vuosi2022.csv \
-y 2022 -o /Users/myliheik/Documents/GISdata/satotutkimus/training-2022/ -s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 4100

# 2022 puutuva rapsi Mirvan uudesta datasta:
python ../python/00-preprecessing-training-set.py -i /Users/myliheik/Documents/GISdata/Kasvulohkot2022/kasvulohkot2022-mod.shp \
-j /Users/myliheik/Documents/GISdata/satotutkimus/SATO_VUODET_2016_2023_Marialle.csv -y 2022 \
-o /Users/myliheik/Documents/GISdata/satotutkimus/training-2022/ -s /Users/myliheik/Documents/myCROPYIELD/references/ -g 0.5 -f 4200


# Pinjan custom SQL for missing 2022 crops, from table:
# stat_sato on skeema, lukedb2prod.ns.luke.fi tietokannan osoite

select sv.tilatunnus, sv.kasitekoodi1, sk.kod_selite_fi1, sv.kasitekoodi2, sk.kod_selite_fi2, sv.kasitekoodi3, sk.kod_selite_fi3, sv.numeroarvo from stat_sato.sato_v sv left join stat_sato.sato_koodit sk on sv.kasitekoodi1 = kasitekoodi1 and sv.kasitekoodi2 = sk.kod_kasitekoodi2 and sv.kasitekoodi3 = sk.kod_kasitekoodi3 where sv.vuosi = 2022 and sv.kasitekoodi2 in ('14545', '20941') and kasitekoodi3 in ('61197', '386579', '387139', '387019', '387023', '61223');




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
    kasvulohko.rename(columns={"KVI_KASVIKOODI": "KASVIKOODI", "KVI_KASVIK": "KASVIKOODI", "MAATILA_TUNNUS": "MAATILA_TU", "KLILM_TUNN": "KLILM_TUNNUS"
                              }, inplace=True)
    #print(kasvulohko.columns)
    
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
    dataSato0 = pd.read_csv(referencepath)
    #dataSato0 = pd.read_csv(referencepath, sep = ',')
    #dataSato0 = pd.read_csv(referencepath, sep = ';') # ei osaa automaattisesti arvata erotinta :/
    dataSato0.rename(columns={"MTYRI_TILTU": "tiltu", 'VUOSI': 'vuosi', 'knro': 'KUNTA_KNRO_VUOSI'}, inplace = True)
    #print(dataSato0)
    dataSato = dataSato0[dataSato0.vuosi == year]
    return dataSato

def munchAllYields(dataSato, satofpout, year, referencepath):
    # jos on kylvetty ala pajon suurempi kuin korjattu, niin sitten on ongelma:
    dataSato['erotus1110'] = (dataSato['syysvehna_kylvo'] - dataSato['syysvehna_ala'])/dataSato['syysvehna_kylvo']
    dataSato['erotus1120'] = (dataSato['kevatvehna_kylvo'] - dataSato['kevatvehna_ala'])/dataSato['kevatvehna_kylvo']
    dataSato['erotus1230'] = (dataSato['ruis_kylvo'] - dataSato['ruis_ala'])/dataSato['ruis_kylvo']
    dataSato['erotus1310'] = (dataSato['rehuohra_kylvo'] - dataSato['rehuohra_ala'])/dataSato['rehuohra_kylvo']
    dataSato['erotus1320'] = (dataSato['mallasohra_kylvo'] - dataSato['mallasohra_ala'])/dataSato['mallasohra_kylvo']
    dataSato['erotus1400'] = (dataSato['kaura_kylvo'] - dataSato['kaura_ala'])/dataSato['kaura_kylvo']
    
    dataSato['erotus2110'] = (dataSato['ruokaherne_kylvo'] - dataSato['ruokaherne_ala'])/dataSato['ruokaherne_kylvo']
    dataSato['erotus2120'] = (dataSato['rehuherne_kylvo'] - dataSato['rehuherne_ala'])/dataSato['rehuherne_kylvo']
    dataSato['erotus2200'] = (dataSato['harkapapu_kylvo'] - dataSato['harkapapu_ala'])/dataSato['harkapapu_kylvo']
    dataSato['erotus3110'] = (dataSato['ruokaperuna_kylvo'] - dataSato['ruokaperuna_ala'])/dataSato['ruokaperuna_kylvo']
    dataSato['erotus3120'] = (dataSato['ruokateolperuna_kylvo'] - dataSato['ruokateolperuna_ala'])/dataSato['ruokateolperuna_kylvo']
    dataSato['erotus3130'] = (dataSato['tarkkelysperuna_kylvo'] - dataSato['tarkkelysperuna_ala'])/dataSato['tarkkelysperuna_kylvo']
    dataSato['erotus3140'] = (dataSato['muuperuna_kylvo'] - dataSato['muuperuna_ala'])/dataSato['muuperuna_kylvo']
    dataSato['erotus3150'] = (dataSato['varhaisperuna_kylvo'] - dataSato['varhaisperuna_ala'])/dataSato['varhaisperuna_kylvo']
    

    dataSato['farm_ID'] = dataSato.tiltu.astype(int) # Remove leading zeros
    
    if 'Satotiedot_2022_Marialle.csv-mod' in referencepath: # alat hehtaareina!

        dataSato['y1110'] = dataSato.syysvehna_sato / (dataSato.syysvehna_ala)
        dataSato['y1120'] = dataSato.kevatvehna_sato / (dataSato.kevatvehna_ala)
        dataSato['y1310'] = dataSato.rehuohra_sato / (dataSato.rehuohra_ala)
        dataSato['y1320'] = dataSato.mallasohra_sato / (dataSato.mallasohra_ala)

        dataSato['y1230'] = dataSato.ruis_sato / (dataSato.ruis_ala) 

        dataSato['y1400'] = dataSato.kaura_sato / (dataSato.kaura_ala)

        #dataSato['y4100'] = dataSato.rypsi_sato / (dataSato.rypsi_ala) # not included in the file
        #dataSato['y4200'] = dataSato.rapsi_sato / (dataSato.rapsi_ala) # not included in the file

        dataSato['y2110'] = dataSato.ruokaherne_sato / (dataSato.ruokaherne_ala)
        dataSato['y2120'] = dataSato.rehuherne_sato / (dataSato.rehuherne_ala)

        dataSato['y2200'] = dataSato.harkapapu_sato / (dataSato.harkapapu_ala)

        dataSato['y3110'] = dataSato.ruokaperuna_sato / (dataSato.ruokaperuna_ala)
        dataSato['y3120'] = dataSato.ruokateolperuna_sato / (dataSato.ruokateolperuna_ala)
        dataSato['y3130'] = dataSato.tarkkelysperuna_sato / (dataSato.tarkkelysperuna_ala)
        dataSato['y3140'] = dataSato.muuperuna_sato / (dataSato.muuperuna_ala)
        dataSato['y3150'] = dataSato.varhaisperuna_sato / (dataSato.varhaisperuna_ala)
        
        df2 = pd.wide_to_long(dataSato, stubnames='y', i=['farm_ID', 'vuosi', 'KUNTA_KNRO_VUOSI'], j='croptype').reset_index()
        cols =  df2.columns[df2.columns.str.startswith('erotus')].tolist()
        df = df2[['tiltu', 'farm_ID', 'vuosi',  'croptype', 'y', 'KUNTA_KNRO_VUOSI'] + cols].dropna(subset = ['y'])


        # filteröidään pois ne joilla erotus > 0.2 tai < -0.2 eli 20%:n satomenetys:
        df = df[~((df['croptype'] == 1110) & (abs(df['erotus1110']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1120) & (abs(df['erotus1120']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1230) & (abs(df['erotus1230']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1310) & (abs(df['erotus1310']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1320) & (abs(df['erotus1320']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1400) & (abs(df['erotus1400']) > 0.2))].copy()

        df = df[~((df['croptype'] == 2110) & (abs(df['erotus2110']) > 0.2))].copy()
        df = df[~((df['croptype'] == 2120) & (abs(df['erotus2120']) > 0.2))].copy()
        df = df[~((df['croptype'] == 2200) & (abs(df['erotus2200']) > 0.2))].copy()
        df = df[~((df['croptype'] == 3110) & (abs(df['erotus3110']) > 0.2))].copy()
        df = df[~((df['croptype'] == 3130) & (abs(df['erotus3130']) > 0.2))].copy()
        df = df[~((df['croptype'] == 3120) & (abs(df['erotus3120']) > 0.2))].copy()
        df = df[~((df['croptype'] == 3150) & (abs(df['erotus3150']) > 0.2))].copy()
        #df = df[~((df['croptype'] == 4100) & (abs(df['erotus4100']) > 0.2))].copy()
        #df = df[~((df['croptype'] == 4200) & (abs(df['erotus4200']) > 0.2))].copy()
        
        
    else: # unit is usually acres but not always:
        dataSato['erotus4200'] = (dataSato['rapsi_kylvo'] - dataSato['rapsi_ala'])/dataSato['rapsi_kylvo']
        dataSato['erotus4100'] = (dataSato['rypsi_kylvo'] - dataSato['rypsi_ala'])/dataSato['rypsi_kylvo']
        
        dataSato['y1110'] = dataSato.syysvehna_sato / (dataSato.syysvehna_ala /100)
        dataSato['y1120'] = dataSato.kevatvehna_sato / (dataSato.kevatvehna_ala /100)
        dataSato['y1310'] = dataSato.rehuohra_sato / (dataSato.rehuohra_ala /100)
        dataSato['y1320'] = dataSato.mallasohra_sato / (dataSato.mallasohra_ala /100)
        
        if year == 2023:
            dataSato['y1230'] = dataSato.ruis_sato / (dataSato.ruis_ala) 
            
        else:
            dataSato['y1230'] = dataSato.ruis_sato / (dataSato.ruis_ala /100) 
            
        dataSato['y1400'] = dataSato.kaura_sato / (dataSato.kaura_ala /100)

        
        dataSato['y4100'] = dataSato.rypsi_sato / (dataSato.rypsi_ala /100)
        dataSato['y4200'] = dataSato.rapsi_sato / (dataSato.rapsi_ala /100)
        
        if year == 2023:       
            dataSato['y2110'] = dataSato.ruokaherne_sato / (dataSato.ruokaherne_ala)
            dataSato['y2120'] = dataSato.rehuherne_sato / (dataSato.rehuherne_ala)
            dataSato['y2200'] = dataSato.harkapapu_sato / (dataSato.harkapapu_ala)
        else:
            dataSato['y2110'] = dataSato.ruokaherne_sato / (dataSato.ruokaherne_ala/100)
            dataSato['y2120'] = dataSato.rehuherne_sato / (dataSato.rehuherne_ala/100)
            dataSato['y2200'] = dataSato.harkapapu_sato / (dataSato.harkapapu_ala/100) 
            
        dataSato['y3110'] = dataSato.ruokaperuna_sato / (dataSato.ruokaperuna_ala/100)
        dataSato['y3120'] = dataSato.ruokateolperuna_sato / (dataSato.ruokateolperuna_ala/100)
        dataSato['y3130'] = dataSato.tarkkelysperuna_sato / (dataSato.tarkkelysperuna_ala/100)
        dataSato['y3140'] = dataSato.muuperuna_sato / (dataSato.muuperuna_ala/100)
        dataSato['y3150'] = dataSato.varhaisperuna_sato / (dataSato.varhaisperuna_ala/100)
        
        
    

        df2 = pd.wide_to_long(dataSato, stubnames='y', i=['farm_ID', 'vuosi', 'KUNTA_KNRO_VUOSI'], j='croptype').reset_index()
        cols =  df2.columns[df2.columns.str.startswith('erotus')].tolist()
        df = df2[['tiltu', 'farm_ID', 'vuosi',  'croptype', 'y', 'KUNTA_KNRO_VUOSI'] + cols].dropna(subset = ['y'])


        # filteröidään pois ne joilla erotus > 0.2 tai < -0.2 eli 20%:n satomenetys:
        df = df[~((df['croptype'] == 1110) & (abs(df['erotus1110']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1120) & (abs(df['erotus1120']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1230) & (abs(df['erotus1230']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1310) & (abs(df['erotus1310']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1320) & (abs(df['erotus1320']) > 0.2))].copy()
        df = df[~((df['croptype'] == 1400) & (abs(df['erotus1400']) > 0.2))].copy()

        df = df[~((df['croptype'] == 2110) & (abs(df['erotus2110']) > 0.2))].copy()
        df = df[~((df['croptype'] == 2120) & (abs(df['erotus2120']) > 0.2))].copy()
        df = df[~((df['croptype'] == 2200) & (abs(df['erotus2200']) > 0.2))].copy()
        df = df[~((df['croptype'] == 3110) & (abs(df['erotus3110']) > 0.2))].copy()
        df = df[~((df['croptype'] == 3130) & (abs(df['erotus3130']) > 0.2))].copy()
        df = df[~((df['croptype'] == 3120) & (abs(df['erotus3120']) > 0.2))].copy()
        df = df[~((df['croptype'] == 3150) & (abs(df['erotus3150']) > 0.2))].copy()
        df = df[~((df['croptype'] == 4100) & (abs(df['erotus4100']) > 0.2))].copy()
        df = df[~((df['croptype'] == 4200) & (abs(df['erotus4200']) > 0.2))].copy()


    print(f"Parcels per crop type: \n {df[['croptype', 'vuosi']].groupby(['croptype', 'vuosi']).value_counts()}")
    
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
    
    df3 = df.groupby(['tiltu', 'croptype'], as_index=False, sort=False).agg({'y':'mean', 'farm_ID':'first', 'vuosi':'first',
                                                              'croptype':'first', 'KUNTA_KNRO_VUOSI':'first'})

    df3['farmID'] = df3['vuosi'].astype(str) + '_' + df3['farm_ID'].astype(str) + '_' + df3['croptype'].astype(str) 
             
    df3['farmID2'] = df3['vuosi'].astype(str) + '_' + df3['farm_ID'].astype(str) + '_' + df3['croptype'].astype(str) + '_' + df3.y.astype(int).astype(str)
    satoy = df3[['tiltu', 'farmID', 'farmID2', 'vuosi', 'KUNTA_KNRO_VUOSI', 'croptype', 'y']]
    satoy['y'] = satoy.y.astype(int)
    
    #outputfile = os.path.join(satofpout, 'references-' + year + '.csv')
    #print(f'Saving yields to {outputfile}')
    #satoy.drop(columns = ['tiltu', 'vuosi']).to_csv(outputfile, index = False)
             
    return satoy.drop(columns = ['tiltu', 'vuosi'])
    
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

    cropss = crops.get(setti)

    for crop in cropss:
        cropid = cropids.get(crop)
        # jos on kylvetty ala pajon suurempi kuin korjattu, niin sitten on ongelma:
        dataSato['erotus' + cropid] = (dataSato[crop + '_kylvo'] - dataSato[crop + '_ala'])/dataSato[crop + '_kylvo']
        
        if (year == 2023) & (crop in ['ruis', 'herne', 'ruokaherne', 'rehuherne', 'harkapapu']):
            dataSato['y' + cropid] = dataSato[crop + '_sato'] / (dataSato[crop + '_ala']) # hectares
            
        else:    
            dataSato['y' + cropid] = dataSato[crop + '_sato'] / (dataSato[crop + '_ala'] /100) # acres

            
        # filteröidään pois ne joilla erotus > 0.2 tai < -0.2 eli 20%:n satomenetys:
        dataSato = dataSato[~(abs(dataSato['erotus' + cropid]) > 0.2)].copy()
        #print(len(dataSato['y' + cropid][~dataSato['y' + cropid].isna()]))

    dataSato['farm_ID'] = dataSato.tiltu.astype(int) # Remove leading zeros

    df2 = pd.wide_to_long(dataSato, stubnames='y', i=['farm_ID', 'vuosi', 'KUNTA_KNRO_VUOSI'], j='croptype').reset_index()
    cols =  df2.columns[df2.columns.str.startswith('erotus')].tolist()
    df = df2[['tiltu', 'farm_ID', 'vuosi',  'croptype', 'y', 'KUNTA_KNRO_VUOSI'] + cols].dropna(subset = ['y'])



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
    
    # filter:
    df2 = df[df['croptype'] == int(setti)]
    df3 = df2.groupby('tiltu', as_index=False, sort=False).agg({'y':'mean', 'farm_ID':'first', 'vuosi':'first',
                                                              'croptype':'first', 'KUNTA_KNRO_VUOSI':'first'})
    #print(df3)
    df3['farmID'] = df3['vuosi'].astype(str) + '_' + df3['farm_ID'].astype(str) + '_' + df3['croptype'].astype(str) 
    df3['farmID2'] = df3['vuosi'].astype(str) + '_' + df3['farm_ID'].astype(str) + '_' + df3['croptype'].astype(str) + '_' + df3.y.astype(int).astype(str)
    satoy = df3[['tiltu', 'farmID', 'farmID2', 'vuosi', 'KUNTA_KNRO_VUOSI', 'croptype', 'y']]
    satoy['y'] = satoy.y.astype(int)
    
    return satoy.drop(columns = ['tiltu', 'vuosi'])

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
    #print(dataByFarm2)
    print(f'How many common farmIDs was found: {len(dataByFarm2)} {len(dataByFarm), len(dataByFarm2)}')
    print(f'The share (%) of farmIDs not found: {(len(dataByFarm) - len(dataByFarm2))/len(dataByFarm)}')
    
    outputfile2 = os.path.join(out_dir_path, 'satotilat-' + str(year) + '-' + '-'.join(setti) + '.shp')  
    print(f'Saving geometries to {outputfile2}')   
    dataByFarm3 = dataByFarm2[['farmID2', 'geometry']]
    dataByFarm3.rename(columns = {"farmID2": "farmID"}, inplace = True)
        
    dataByFarm3[['farmID', 'geometry']].to_file(driver = 'ESRI Shapefile', filename = outputfile2)

    # Tallennetaan farmID muotoon VUOSI_farm_CROPTYPE_yield ja referenssitiedostoon: farmID, KUNTA_KNRO_VUOSI, croptype, y

  
    
# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputpath:
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n00-preprecessing-training-set.py')        
        print(f'\nLPIS data in: {args.inputpath}')
        
        # directory for output:
        out_dir_path = args.outputshppath
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)
        
        satofpout = args.satofpout
        Path(satofpout).mkdir(parents=True, exist_ok=True)

        dataSato = readRefe(args.referencepath, args.year)

        # READ LPIS, filter out too small parcels and select only relevant crop types:
        kasvulohko = readLPIS(args.inputpath, dataSato, args.setti, args.year, args.filter)
        
        if args.setti is None: # make reference yields
            satoy = munchAllYields(dataSato, args.satofpout, args.year, args.referencepath)
            
        elif 'Satotiedot_2022_Marialle.csv-mod' in args.referencepath: # alat hehtaareina! Pakko käyttää tätä funktiota, tekee kaikki saatavilla olevat.
            satoy = munchAllYields(dataSato, args.satofpout, args.year, args.referencepath)
            
        else:   
            dflist = []
            for crop in args.setti:
                dflist.append(munchCropYield(crop, dataSato, args.year))
                
            satoy = pd.concat(dflist) 
          
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






    