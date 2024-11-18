"""
2022-10-27


    pvm3 = 2022-09-02
    vuosi = 2022
    crop = 1120

@myGIS

RUN:
python makeMaps-withRegional-predictions.py -v 2022 -c 1110 -d 2022-09-02 -o /Users/myliheik/Documents/mySISA/img
python makeMaps-withRegional-predictions.py -v 2022 -c 1120 -d 2022-09-02 -o /Users/myliheik/Documents/mySISA/img
python makeMaps-withRegional-predictions.py -v 2022 -c 1230 -d 2022-09-02 -o /Users/myliheik/Documents/mySISA/img
python makeMaps-withRegional-predictions.py -v 2022 -c 1310 -d 2022-09-02 -o /Users/myliheik/Documents/mySISA/img
python makeMaps-withRegional-predictions.py -v 2022 -c 1320 -d 2022-09-02 -o /Users/myliheik/Documents/mySISA/img
python makeMaps-withRegional-predictions.py -v 2022 -c 1400 -d 2022-09-02 -o /Users/myliheik/Documents/mySISA/img


"""

import pandas as pd
import geopandas as gpd
import argparse
import textwrap
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os.path

Dict = dict({'1110': 'Autumn wheat', '1120': 'Spring wheat', '1230': 'Rye',
            '1310': 'Feed barley', '1320': 'Malting barley', '1300': 'Barley', '1400': 'Oats'})

def makeSuomi():
    
    global suomi
    global valitut2
    
    fp = '/Users/myliheik/Documents/GISdata/tukialueet2013-YKJ-KKJkaista3-EPSG2393/tukialueet.shp'
    gdf0 = gpd.read_file(fp)
    gdf0.crs = '+proj=tmerc +lat_0=0 +lon_0=27 +k=1 +x_0=3500000 +y_0=0 +ellps=intl +towgs84=-96.062,-82.428,-121.753,4.801,0.345,-1.376,1.496 +units=m +no_defs'
    gdf0['temp'] = 1
    suomi = gdf0.dissolve(by='temp')

    # Kunnat kartta:
    fp = '/Users/myliheik/Documents/GISdata/mml/hallintorajat_milj_tk/Hallintorajat2020-teemakartoille-ei-merialueita/kunnat_2020_milj.shp'
    kunnat = gpd.read_file(fp)
    valitut = kunnat[kunnat['NATCODE'].isin(['233', '408', '748', '430', '434', '286', '607', '297', '636', '638'])]
    valitut2 = valitut.to_crs(gdf0.crs)
    
    return suomi, valitut2


def readPreds(crop, vuosi, pvm3):
    


    fpath = '/Users/myliheik/Documents/myCROPYIELD/scratch/project_2001253/cropyield2022/cloudy/predictions/' + pvm3 + '/' + crop + '-' + vuosi + '/TCNPreds.pkl'
    fpfarmids = '/Users/myliheik/Documents/myCROPYIELD/scratch/project_2001253/cropyield2022/cloudy/dataStack/farmID_' + crop + '-' + vuosi + '.pkl'
    preds = pd.read_pickle(fpath)
    farmids = pd.read_pickle(fpfarmids)
    df = pd.DataFrame(preds[:,:,-1])
    df.columns = ['day_' + str(i) for i in range(len(df.columns))]
    dfIDs = pd.DataFrame(farmids, columns = ['farmID'])
    dfIDs2 = dfIDs['farmID'].str.split('_', expand = True)
    dfIDs2.columns = ['Year', 'farmID', 'Municipality', 'Crop']

    dfCrop = pd.concat([dfIDs2, df], axis = 1)

    return dfCrop

    
def readKunta():
    fp = '/Users/myliheik/Documents/myCROPYIELD/dataSatotilasto/kunta_1_20220101.csv-mod'
    df = pd.read_csv(fp, sep = ';')
    return df
    

def plottingMap(crop, vuosi, dfCrop):
    # locations:
    #Salo = dfCrop[dfCrop.Municipality == '734']
    
    colors = [sns.color_palette("ch:start=.2,rot=-.3")[2], "lightgrey", sns.color_palette("ch:start=.2,rot=-.3")[1], sns.color_palette("ch:start=.2,rot=-.3")[0]]
   
    Kauhava = dfCrop[dfCrop.Municipality == '233'] 
    if not Kauhava.empty: 
        Kauhava['id'] = Kauhava.index
        Kauhava2 = Kauhava.loc[:, Kauhava.columns.str.startswith(('day', 'id'))]
        Kauhava3 = pd.wide_to_long(Kauhava2, stubnames = 'day_', i = 'id', j = 'Date')/1000
        Kauhava3.columns = ['Predicted yield']
    

    Lapua = dfCrop[dfCrop.Municipality == '408'] 
    if not Kauhava.empty:
        Lapua['id'] = Lapua.index
        Lapua2 = Lapua.loc[:, Lapua.columns.str.startswith(('day', 'id'))]
        Lapua3 = pd.wide_to_long(Lapua2, stubnames = 'day_', i = 'id', j = 'Date')/1000
        Lapua3.columns = ['Predicted yield']
    
    Siikajoki = dfCrop[dfCrop.Municipality == '748'] 
    Siikajoki['id'] = Siikajoki.index
    Siikajoki2 = Siikajoki.loc[:, Siikajoki.columns.str.startswith(('day', 'id'))]
    Siikajoki3 = pd.wide_to_long(Siikajoki2, stubnames = 'day_', i = 'id', j = 'Date')/1000
    Siikajoki3.columns = ['Predicted yield']

    Loimaa = dfCrop[dfCrop.Municipality == '430'] 
    Loimaa['id'] = Loimaa.index
    Loimaa2 = Loimaa.loc[:, Loimaa.columns.str.startswith(('day', 'id'))]
    Loimaa3 = pd.wide_to_long(Loimaa2, stubnames = 'day_', i = 'id', j = 'Date')/1000
    Loimaa3.columns = ['Predicted yield']  
    
    Loviisa = dfCrop[dfCrop.Municipality == '434'] 
    Loviisa['id'] = Loviisa.index
    Loviisa2 = Loviisa.loc[:, Loviisa.columns.str.startswith(('day', 'id'))]
    Loviisa3 = pd.wide_to_long(Loviisa2, stubnames = 'day_', i = 'id', j = 'Date')/1000
    Loviisa3.columns = ['Predicted yield']
    
    Kouvola = dfCrop[dfCrop.Municipality == '286'] 
    Kouvola['id'] = Kouvola.index
    Kouvola2 = Kouvola.loc[:, Kouvola.columns.str.startswith(('day', 'id'))]
    Kouvola3 = pd.wide_to_long(Kouvola2, stubnames = 'day_', i = 'id', j = 'Date')/1000
    Kouvola3.columns = ['Predicted yield']
    
    Polvijärvi = dfCrop[dfCrop.Municipality == '607'] 
    if not Polvijärvi.empty:
        Polvijärvi['id'] = Polvijärvi.index
        Polvijärvi2 = Polvijärvi.loc[:, Polvijärvi.columns.str.startswith(('day', 'id'))]
        Polvijärvi3 = pd.wide_to_long(Polvijärvi2, stubnames = 'day_', i = 'id', j = 'Date')/1000
        Polvijärvi3.columns = ['Predicted yield']

    Kuopio = dfCrop[dfCrop.Municipality == '297'] 
    Kuopio['id'] = Kuopio.index
    Kuopio2 = Kuopio.loc[:, Kuopio.columns.str.startswith(('day', 'id'))]
    Kuopio3 = pd.wide_to_long(Kuopio2, stubnames = 'day_', i = 'id', j = 'Date')/1000
    Kuopio3.columns = ['Predicted yield']

    Pöytyä = dfCrop[dfCrop.Municipality == '636'] 
    Pöytyä['id'] = Pöytyä.index
    Pöytyä2 = Pöytyä.loc[:, Pöytyä.columns.str.startswith(('day', 'id'))]
    Pöytyä3 = pd.wide_to_long(Pöytyä2, stubnames = 'day_', i = 'id', j = 'Date')/1000
    Pöytyä3.columns = ['Predicted yield']
    
    # Porvoo 638
    Porvoo = dfCrop[dfCrop.Municipality == '638'] 
    Porvoo['id'] = Porvoo.index
    Porvoo2 = Porvoo.loc[:, Porvoo.columns.str.startswith(('day', 'id'))]
    Porvoo3 = pd.wide_to_long(Porvoo2, stubnames = 'day_', i = 'id', j = 'Date')/1000
    Porvoo3.columns = ['Predicted yield']

    
    
    
    
    
    
    
    
    
    plt.rcParams['text.usetex'] = True

    fig = plt.figure(figsize=(6,10))
    ax_map = fig.add_axes([0, 0, 1, 1])
    suomi.plot(ax=ax_map, color=colors) #['#C62828', '#283593', '#283593', '#FF9800'])
    ax_map.set_axis_off()

    plt.rcParams.update({'font.size': 10})

    lat, lon = 6651787, 3181486
    #colors = ['#C62828', '#283593', '#283593', '#FF9800', '#FF9800']
    #ax_bar = fig.add_axes([0.5*(1+lon/180) , 0.5*(1+lat/90) , 0.05, 0.05])
    ax_barC = fig.add_axes([0.1, 0.45, 0.4, 0.15])
    #ax_barC = sns.barplot(x="Type", y="C", data=df)
    #ax_bar.bar([1, 2, 3, 4, 5], df['A'], color=colors, label = df['Type'].tolist())
    ax_barC = sns.lineplot(data=Siikajoki3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
    #ax_barC.set(ylim=(2, 6), xticks=[1, 43, 73, 104])
    #ax_barC.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
    ax_barC.set(title = 'Siikajoki')
    #ax_barC.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
    ax_barC.set(ylim=(2, 6), xticklabels=[], xlabel=None)
    ax_barC.set_xlabel(None)
    ax_barC.set_ylabel(None)
    ax_barC.tick_params(bottom=False)
    #ax_barC.patch.set_facecolor('red')
    ax_barC.patch.set_facecolor(None)
    ax_barC.patch.set_alpha(0)
    ax_barC.spines['right'].set_visible(False)
    ax_barC.spines['top'].set_visible(False)
    valitut2.iloc[2:3].plot(ax=ax_map, color='red') # Siikajoki



    ax_barB = fig.add_axes([0.4, -0.1, 0.4, 0.15])
    ax_barB = sns.lineplot(data=Loviisa3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
    ax_barB.set(ylim=(2, 6), xticks=[1, 43, 73, 104])
    #ax_barB.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
    ax_barB.set(ylim=(2, 6), xticklabels=[], xlabel=None)
    ax_barB.tick_params(bottom=False)
    ax_barB.set(title = 'Loviisa')
    ax_barB.patch.set_facecolor(None)
    ax_barB.set_xlabel(None)
    #ax_barB.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
    ax_barB.set_ylabel(None)
    ax_barB.patch.set_alpha(0)
    ax_barB.spines['right'].set_visible(False)
    ax_barB.spines['top'].set_visible(False)
    valitut2.iloc[5:6].plot(ax=ax_map, color='red') # Loviisa




    ax_barA = fig.add_axes([-0.2, 0.06, 0.4, 0.15])
    ax_barA = sns.lineplot(data=Loimaa3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
    ax_barA.set(ylim=(2, 6), xticks=[1, 43, 73, 104])
    #ax_barA.tick_params(bottom=False)
    ax_barA.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
    ax_barA.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
    #ax_barA.set(ylim=(2, 6), xticklabels=[], xlabel=None)
    ax_barA.patch.set_facecolor(None)
    ax_barA.set(title = 'Loimaa')
    #ax_barA.set_xlabel(None)
    #ax_barA.set_ylabel(None)
    ax_barA.patch.set_alpha(0)
    ax_barA.spines['right'].set_visible(False)
    ax_barA.spines['top'].set_visible(False)
    valitut2.iloc[3:4].plot(ax=ax_map, color='red') # Loimaa


    ax_barA = fig.add_axes([-0.2, 0.06, 0.4, 0.15])
    ax_barA = sns.lineplot(data=Pöytyä3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
    ax_barA.set(ylim=(2, 6), xticks=[1, 43, 73, 104])
    #ax_barA.tick_params(bottom=False)
    ax_barA.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
    ax_barA.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
    #ax_barA.set(ylim=(2, 6), xticklabels=[], xlabel=None)
    ax_barA.patch.set_facecolor(None)
    ax_barA.set(title = 'Loimaa/Pöytyä')
    #ax_barA.set_xlabel(None)
    #ax_barA.set_ylabel(None)
    ax_barA.patch.set_alpha(0)
    ax_barA.spines['right'].set_visible(False)
    ax_barA.spines['top'].set_visible(False)
    valitut2.iloc[4:5].plot(ax=ax_map, color='red') # Pöytyä


    if not Lapua.empty:
        ax_barD = fig.add_axes([-0.1, 0.25, 0.4, 0.15])
        ax_barD = sns.lineplot(data=Lapua3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
        #ax_barD.set(ylim=(2, 6), xticks=[1, 43, 73, 104])
        ax_barD.set(ylim=(2, 6), xticklabels=[], xlabel=None)
        #ax_barD.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
        ax_barD.tick_params(bottom=False)
        ax_barD.set(title = 'Lapua')
        ax_barD.patch.set_facecolor(None)
        ax_barD.set_xlabel(None)
        ax_barD.set_ylabel(None)
        #ax_barD.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
        ax_barD.patch.set_alpha(0)
        ax_barD.spines['right'].set_visible(False)
        ax_barD.spines['top'].set_visible(False)
        valitut2.iloc[8:9].plot(ax=ax_map, color='red') # Lapua


    if not Kauhava.empty:
        ax_barE = fig.add_axes([-0.1, 0.25, 0.4, 0.15])
        ax_barE = sns.lineplot(data=Kauhava3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
        ax_barE.set(ylim=(2, 6))#, xticks=[1, 43, 73, 104])
        #ax_barE.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
        ax_barE.set(ylim=(2, 6), xticklabels=[], xlabel=None)
        ax_barE.tick_params(bottom=False)
        ax_barE.set(title = 'Kauhava/Lapua')
        ax_barE.patch.set_facecolor(None)
        ax_barE.set_xlabel(None)
        #ax_barE.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
        ax_barE.set_ylabel(None)
        ax_barE.patch.set_alpha(0)
        ax_barE.spines['right'].set_visible(False)
        ax_barE.spines['top'].set_visible(False)
        valitut2.iloc[7:8].plot(ax=ax_map, color='red') # Kauhava


    ax_barF = fig.add_axes([0.9, 0.06, 0.4, 0.15])
    #ax_barF = fig.add_axes([0.5, 0.01, 0.4, 0.15])
    #ax_barF = ax_barB
    ax_barF = sns.lineplot(data=Kouvola3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
    ax_barF.set(ylim=(2, 6))#, xticks=[1, 43, 73, 104])
    #ax_barE.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
    ax_barF.set(ylim=(2, 6), xticklabels=[], xlabel=None)
    ax_barF.tick_params(bottom=False)
    ax_barF.set(title = 'Kouvola')
    ax_barF.patch.set_facecolor(None)
    ax_barF.set_xlabel(None)
    #ax_barE.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
    ax_barF.set_ylabel(None)
    ax_barF.patch.set_alpha(0)
    ax_barF.spines['right'].set_visible(False)
    ax_barF.spines['top'].set_visible(False)
    valitut2.iloc[0:1].plot(ax=ax_map, color='red') # Kouvola



    ax_barJ = fig.add_axes([0.4, -0.1, 0.4, 0.15])
    #ax_barJ = ax_barB
    ax_barJ = sns.lineplot(data=Porvoo3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
    ax_barJ.set(ylim=(2, 6))#, xticks=[1, 43, 73, 104])
    #ax_barJ.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
    ax_barJ.set(ylim=(2, 6), xticklabels=[], xlabel=None)
    ax_barJ.tick_params(bottom=False)
    ax_barJ.set(title = 'Porvoo/Loviisa')
    ax_barJ.patch.set_facecolor(None)
    ax_barJ.set_xlabel(None)
    #ax_barJ.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
    ax_barJ.set_ylabel(None)
    ax_barJ.patch.set_alpha(0)
    ax_barJ.spines['right'].set_visible(False)
    ax_barJ.spines['top'].set_visible(False)
    valitut2.iloc[9:10].plot(ax=ax_map, color='red') # Porvoo


    if not Polvijärvi.empty:
        ax_barG = fig.add_axes([0.9, 0.25, 0.4, 0.15])
        ax_barG = sns.lineplot(data=Polvijärvi3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
        ax_barG.set(ylim=(2, 6))#, xticks=[1, 43, 73, 104])
        #ax_barE.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
        ax_barG.set(ylim=(2, 6), xticklabels=[], xlabel=None)
        ax_barG.tick_params(bottom=False)
        ax_barG.set(title = 'Polvijärvi')
        ax_barG.patch.set_facecolor(None)
        ax_barG.set_xlabel(None)
        #ax_barE.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
        ax_barG.set_ylabel(None)
        ax_barG.patch.set_alpha(0)
        ax_barG.spines['right'].set_visible(False)
        ax_barG.spines['top'].set_visible(False)
        valitut2.iloc[1:2].plot(ax=ax_map, color='red') # Polvijärvi



    ax_barK = fig.add_axes([0.9, 0.45, 0.4, 0.15])
    ax_barK = sns.lineplot(data=Kuopio3.reset_index(), x="Date", y="Predicted yield", ci = 'sd')
    ax_barK.set(ylim=(2, 6))#, xticks=[1, 43, 73, 104])
    #ax_barK.set_xticklabels(['May 10', 'Jun 15', 'Jul 15', 'Aug 15'], rotation=45)
    ax_barK.set(ylim=(2, 6), xticklabels=[], xlabel=None)
    ax_barK.tick_params(bottom=False)
    ax_barK.set(title = 'Kuopio')
    ax_barK.patch.set_facecolor(None)
    ax_barK.set_xlabel(None)
    #ax_barK.set_ylabel(r'Predicted yield (t $kg\ ha^{-1}$)', fontsize=10)
    ax_barK.set_ylabel(None)
    ax_barK.patch.set_alpha(0)
    ax_barK.spines['right'].set_visible(False)
    ax_barK.spines['top'].set_visible(False)
    valitut2.iloc[6:7].plot(ax=ax_map, color='red') # Kuopio



    plt.rcParams.update({'font.size': 16, 'font.weight': 'bold'})
    ax_map.annotate(f'Year: {vuosi}', xy=(lon, lat),  xycoords='data',
                xytext=(0, 0.87), textcoords='axes fraction', weight='bold',
                #arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='right', verticalalignment='top',
                )
    ax_map.annotate(f'Crop: {Dict[crop]}', xy=(lon, lat),  xycoords='data',
                xytext=(0, 0.84), textcoords='axes fraction', weight='bold',
                #arrowprops=dict(facecolor='black', shrink=0.05),
                horizontalalignment='right', verticalalignment='top',
                )
    
    plt.tight_layout()
    fp = '/Users/myliheik/Documents/mySISA/img/Map-Regional-predictions-' + crop +  '-' + vuosi + '.png'
    plt.savefig(fp, bbox_inches='tight', dpi=300)
    print(f'Saved img in: {fp}')
    
    
    
    
    
    
    
# main:
def main(args):

    try:
        if not args.outputpath:
            raise Exception('Missing output directory argument. Try --help .')

        print(f'\n20-makeMaps-withRegional-predictions.py')
        print(f'\nMake maps.')
   
        out_dir_path = Path(os.path.expanduser(args.outputpath))
        out_dir_path.mkdir(parents=True, exist_ok=True)
       
        makeSuomi()

        dfCrop = readPreds(args.croptype, args.year, args.date)
        plottingMap(args.croptype, args.year, dfCrop)      
        
        print('Done.')

    except Exception as e:
        print('\n\nUnable to read input or write out results. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-v', '--year',
                        type = str,
                        help = 'Year.',
                        default = '2022')
    parser.add_argument('-c', '--croptype',
                        type = str,
                        help = 'Crop type, e.g. 1120 for spring wheat.',
                        default = '1120')
    parser.add_argument('-o', '--outputpath',
                        type = str,
                        help = 'Directory for output image.',
                        default = '.')
    parser.add_argument('-d', '--date',
                        type = str,
                        help = 'Date.',
                        default = '2022-09-02')
        
    args = parser.parse_args()
    main(args)    





