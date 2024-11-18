"""

23.10.2020 
27.1.2021 updated: replace DOY to order number 1,2,3,4,... during the season. We will need 4 datasets (June, July, August)
19.8.2021 added options 1) to merge given years and data sets, 2) outputdir
1.9.2021 saves in compressed numpy file instead of pickle
15.11.2021 oli törkeä virhe combineAllYears-funktiossa, pitää ajaa uudelleen kaikki
25.11.2021 oli törkeä virhe reshapeAndSave-funktiossa (pivot, reindex, reshape), pitää ajaa uudelleen kaikki
5.11.2022 modified for SISA: farmID -> parcelID
21.3.2023 no need to modify
27.7.2023 oli virhe combineAllYears for loopissa! 

Combine annual stack-files into one array stack.

combineAllYears() reads all annuals into one big dataframe.

reshapeAndSave() pivots the dataframe by parcelID and doy, converts to numpy array, fills with na (-> not ragged) and reshapes into 3D. Saves array and parcelIDs into separate files.

RUN: 

python 07-stack2ARD.py -i /Users/myliheik/Documents/myCROPYIELD/dataStack_annual -o /Users/myliheik/Documents/myCROPYIELD/dataStack/ -f 1400 -y 2018 2019

# with 'time series by rank':
python 07-stack2ARD.py -i /Users/myliheik/Documents/myCROPYIELD/scratch/project_2001253/cropyieldII/cloudy/dataStack_annual -o /Users/myliheik/Documents/myCROPYIELD/scratch/project_2001253/cropyieldII/cloudy/dataStackRank -f 1120 -y 2020 -r

After this into 08-mergeTarget.py and 09-runNN.py.

In Puhti: module load geopandas (Python 3.9.) # earlier also needed: pip install 'pandas==1.1.2' --user

"""
import glob
import os
import pandas as pd
import numpy as np
import pickle

from pathlib import Path

import argparse
import textwrap
from datetime import datetime

import warnings
warnings.filterwarnings('ignore')

###### FUNCTIONS:

def load_intensities(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data

def save_intensities(filename, arrayvalues):
    with open(filename, 'wb+') as outputfile:
        pickle.dump(arrayvalues, outputfile)

def combineAllYears(data_folder3, setti, years):
    # read files in inputdir:
    s = pd.Series(glob.glob(data_folder3 + '/*.pkl'))

    filepaths = [] 

    for filepath in s:
        filename = os.path.basename(filepath)
        for keyword1 in years:
            if setti:
                for keyword2 in setti:
                    if (keyword2 in filename) & (keyword1 in filename):
                        filepaths.append(filepath)
            else:
                filepaths.append(filepath)

    print(filepaths)
    if len(filepaths) > 1:
        # open all chosen years into one dataframe:
        allyears = pd.concat(map(pd.read_pickle, filepaths), sort=False)
    else: # if only one year, one set:
        allyears = pd.read_pickle(filepaths[0])
   
    return allyears  

def reshapeAndSave(full_array_stack, out_dir_path, outputfile, rank):    
    # reshape and save data to 3D:
    print(f"\nLength of the data stack dataframe: {len(full_array_stack)}")

    if rank:
        dateVar = 'doyid'
    else:
        dateVar = 'doy'

    if full_array_stack.isna().any().any():
        print(full_array_stack[full_array_stack.isna().any(axis=1)])
        
    full_array_stack['doyid'] = full_array_stack.groupby(['parcelID', 'band'])['doy'].rank(method="first", ascending=True).astype('int')

    #print(full_array_stack.sort_values(['parcelID', 'doy']).tail(15))
    
    # printtaa esimerkkitila:
    #tmp = full_array_stack[full_array_stack['parcelID'] == '2019_12026885_35VMH'][['parcelID', 'doy', 'band', 'doyid']]
    #print(tmp.sort_values(['doy', 'band']))
    
    # printtaa sellaiset, joilla bin1 on 1:
    #print(len(full_array_stack[full_array_stack['bin1'] == 1]))
    # printtaa sellaiset, joilla bin32 on 1:
    #print(len(full_array_stack[full_array_stack['bin32'] == 1]))
    
    # printtaa sellaiset, joiden rivisumma ei ole 1:
    #print(full_array_stack[full_array_stack.drop(['parcelID', 'doy', 'band', 'doyid'], axis = 1).sum(axis = 1) != 1])
    
    # printtaa näiden rivisummat:
    #tmp = full_array_stack[full_array_stack.drop(['parcelID', 'doy', 'band', 'doyid'], axis = 1).sum(axis = 1) < 1]
    #print(len(tmp)) # jotain pyöristysvirhettä ehkäpä vain
    #print(tmp.drop(['parcelID', 'doy', 'band', 'doyid'], axis = 1).sum(axis = 1))
    
    # Predictions to compare with forecasts: 15.6. eli DOY 166, that is pythonic 165.
    # and 15.7. eli DOY 196 
    # and 15.8. eli DOY 227
    # and the last DOY 243 -> the final state
    
    #june = full_array_stack[full_array_stack['doy'] <= 165]
    #print(june.sort_values(['doy', 'band']).tail(20))
    #print(june['doyid'].value_counts())

    #july = full_array_stack[full_array_stack['doy'] <= 195]
    #august = full_array_stack[full_array_stack['doy'] <= 226]

    
    final = full_array_stack
    #print(final['doyid'].value_counts())
    print(f"There are {len(final.parcelID.str.split('_', expand = True)[1].unique())} unique grid cells")
    print(f"There are {len(final.parcelID.unique())} parcels in the data, note overlapping tiles.")
    
    # Kuinka monta havaintoa per tila koko kesältä, mediaani?
    print("How many observations per farm in one season (median)?: ", float(final[['parcelID', dateVar]].drop_duplicates().groupby(['parcelID']).count().median()))
    # Kuinka monta havaintoa per tila koko kesältä, max?
    print("How many observations per farm in one season (max)?: ", float(final[['parcelID', dateVar]].drop_duplicates().groupby(['parcelID']).count().max()))
    # Kuinka monta havaintoa per tila koko kesältä, min?
    print("How many observations per farm in one season (min)?: ", float(final[['parcelID', dateVar]].drop_duplicates().groupby(['parcelID']).count().min()))

    # koko kausi:
    farms = final.parcelID.nunique()
    doys = final[dateVar].nunique()
    bands = 10
    bins = 32

    if final[['parcelID', 'band', 'doy']].duplicated(keep = False).any():
        print(f"There are {final[['parcelID', 'band', 'doy']].duplicated(keep = False).sum()} duplicates out of {farms} parcels. We take the first obs. only.")
        final2 = final.drop_duplicates(subset=['parcelID', 'band', 'doy'], keep='first')
        final = final2.copy()
        print(f"Are there duplicates anymore: {final[['parcelID', 'band', 'doy']].duplicated(keep = False).any()}")
        #tmp = final[final[['parcelID', 'band', 'doy']].duplicated()]
        #print(f"{tmp.parcelID.nunique()}")
        #print(f"{tmp.band.nunique()}")
        #print(f"{tmp.doy.nunique()}")
        #print(f"{tmp.parcelID.str.split('_', expand=True)}")

    pivoted = final.pivot(index=['parcelID', dateVar], columns='band', values=[*final.columns[final.columns.str.startswith('bin')]])
    m = pd.MultiIndex.from_product([pivoted.index.get_level_values(0).unique(), pivoted.index.get_level_values(1).sort_values().unique()], names=pivoted.index.names)
    pt = pivoted.reindex(m, fill_value = 0)
    finalfinal = pt.to_numpy().reshape(farms, doys, bins, bands).swapaxes(2,3).reshape(farms,doys,bands*bins)
    
    outputfile2 = 'array_' + outputfile
    fp = os.path.join(out_dir_path, outputfile2)
    
    print(f"Shape of the 3D stack dataframe: {finalfinal.shape}")
    print(f"Output into file: {fp}")
    np.savez_compressed(fp, finalfinal)
    #save_intensities(fp, finalfinal)
    
    # save parcelIDs for later merging with target y:
    parcelIDs = pt.index.get_level_values(0).unique().str.rsplit('_',1).str[0].values
    print(f"\n\nNumber of farms: {len(parcelIDs)}")
    outputfile2 = 'parcelID_' + outputfile + '.pkl'
    fp = os.path.join(out_dir_path, outputfile2)
    print(f"Output parcelIDs in file: {fp}")
    save_intensities(fp, parcelIDs)
    

    
def main(args):
    
    try:
        if not args.outdir or not args.ylist:
            raise Exception('Missing output dir argument or dataset year. Try --help .')

        print(f'\n\n07-stack2ARD.py')
        print(f'\nInput files in {args.inputdir}')

        # directory for input, i.e. annual results:
        data_folder3 = args.inputdir
        
        # directory for outputs:
        out_dir_path = args.outdir
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)
        
        # years:
        years = args.ylist
        setti = args.setti
        
        # outputfilename:
        #outputfile = '-'.join(setti) + '-' + '-'.join(years) + '.pkl'
        if setti:
            outputfile = '-'.join(setti) + '-' + '-'.join(years)
        else:
            outputfile = '-'.join(years)
        

                
        print("\nPresuming preprocessing done earlier. If not done previously, please, run with histo2stack.py first!")

        print("\nCombining the years and data sets...")
        allyears = combineAllYears(data_folder3, setti, years)
        reshapeAndSave(allyears, out_dir_path, outputfile, args.rank)
        

    except Exception as e:
        print('\n\nUnable to read input or write out results. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputdir',
                        type=str,
                        help='Name of the input directory (where annual histogram dataframes are).',
                        default='.')
    parser.add_argument('-o', '--outdir',
                        type=str,
                        help='Name of the output directory.',
                        default='.')
    # is not true: cannot combine multiple data sets (crops), because parcelID does not hold crop information -> duplicated parcelIDs  
    parser.add_argument('-f', '--setti', action='store', dest='setti',
                         type=str, nargs='*', default=None,
                         help='Name of the data set. Can be also multiple. E.g. -f 1310 1320.')
    #parser.add_argument('-f', '--setti', 
    #                    type=str,
    #                    default=['1400'],
    #                    help='Name of the data set. E.g. -f 1310.')
    parser.add_argument('-y', '--years', action='store', dest='ylist',
                       type=str, nargs='*', default=['2018', '2019', '2020', '2021'],
                       help="Optionally e.g. -y 2018 2019, default all")
    
    parser.add_argument('-r', '--rank',
                        help='If saving time series by rank of days.',
                        default=False,
                        action='store_true')
        
    args = parser.parse_args()
    main(args)



