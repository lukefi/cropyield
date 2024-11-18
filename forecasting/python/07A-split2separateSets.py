"""
2022-03-20 MY
5.11.2022 modified for SISA: farmID -> parcelID
19.6.2024 new parcelID format: 'YEAR_parcel_plantID_MAAKUNTA_KUNTA_PALA_TILE'

When preprocessing all data sets merged, at this point we need to separate them.

Works for one year only!

RUN:
python 07A-split2separateSets.py -i /Users/myliheik/Documents/myCROPYIELD/dataStack_annual -y 2021



"""

import glob
import os
import pandas as pd
import numpy as np
import pickle

from pathlib import Path

import argparse
import textwrap


###### FUNCTIONS:

def save_intensities(filename, arrayvalues):
    with open(filename, 'wb+') as outputfile:
        pickle.dump(arrayvalues, outputfile)

def splitDataset(data_folder3, year):
    # read file in inputdir:
    data = pd.read_pickle(os.path.join(data_folder3, year + '.pkl'))
    data['dataset'] = data['parcelID'].str.rsplit('_', 5).str[1]   # YEAR_parcel_plantID_MAAKUNTA_KUNTA_PALA_TILE
    setit = data['dataset'].drop_duplicates()

    for setti in setit:
        rowmask = data['dataset'] == setti
        
        
        filename = os.path.join(data_folder3, setti + '_' + year + '.pkl')
        
        if os.path.exists(os.path.join(data_folder3, setti + '_' + year + '.pkl')):
            print(f"File {filename} already exists, but we overwrite!")
            save_intensities(filename, data[rowmask].drop('dataset', axis = 1))
        else:
            print(f'Saving data set {setti} in {filename}')
            save_intensities(filename, data[rowmask].drop('dataset', axis = 1))
            
            

def main(args):
    
    try:
        if not args.inputdir or not args.year:
            raise Exception('Missing input dir argument or year. Try --help .')

        print(f'\n\n07A-split2separateSets.py')
        print(f'\nInput files in {args.inputdir}')
        
        print("\nPresuming preprocessing done earlier. If not done previously, please, run with histo2stack.py first!")

        print("\nSeparating data sets...")

        # directory for input, i.e. annual results:
        data_folder3 = args.inputdir
        year = args.year
        
        splitDataset(data_folder3, year)
        

        print("\nDone. After this run 07-stack2ARD.py.")     


        

    except Exception as e:
        print('\n\nUnable to read input or write out results. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputdir',
                        type=str,
                        help='Name of the input directory (where annual histogram dataframe is).',
                        default='.')

    parser.add_argument('-y', '--year',
                        type=str,
                        help='The year to process')
        
    args = parser.parse_args()
    main(args)



