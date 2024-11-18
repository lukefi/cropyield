"""
12.4.2024 MY 

From farmID separate target y. 

RUN:

python 08-makeTarget.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack/ -y 2023

"""
import pandas as pd
import numpy as np
import pickle
import os.path
from pathlib import Path
import argparse
import textwrap
import re
import glob
import utils

# FUNCTIONS:
        
def makeTarget(inputpath, out_dir_path):
    # read array:
    arrayfile = utils.load_npintensities(inputpath)
    # read farmIDs:
    farmid = utils.readTargetID(inputpath)
    setti = utils.parse_xpath(inputpath)
    print(setti)
    fp1 = os.path.join(out_dir_path, 'y_' + setti + '.pkl')
    fp2 = os.path.join(out_dir_path, 'farmID_' + setti + '.pkl')
    fp3 = os.path.join(out_dir_path, inputpath.split('/')[-1])

    idsdf = pd.DataFrame(farmid)
    idsdf.columns = ['farmID']    
    idsdf['y'] = idsdf['farmID'].str.rsplit('_', 3).str[3] # When farmID: YEAR_PARCELID_CROPTYPE_YIELD_TILE

    print(idsdf.head())

    if idsdf['y'].isna().any():
        print(f'There are NAs!')
        # this means, some y not found. Let's filter also array and farmID.
        print(f"There are {idsdf['y'].isna().sum()} NAs.")
        print(f"They are: \n {idsdf[idsdf['y'].isna()]}")
        #print(arrayfile.shape, farmid.shape, len(targets))
        rowmaskNAs = np.array(idsdf['y'].isna())

        arrayfileClear = arrayfile[~rowmaskNAs, :, :]
        farmidClear = idsdf['farmID'][~rowmaskNAs]
        yClear = idsdf['y'][~rowmaskNAs]
              
        print(f'Saving filtered data.')

        print(f'Saving target y to {fp1}.')
        utils.save_intensities(fp1, yClear)
        
        print(f'Saving farmID to {fp2}.')
        utils.save_intensities(fp2, farmidClear)
        
        print(f'Saving arrayfiles into {fp3}.')
        np.savez_compressed(fp3, arrayfileClear)    
        
        print(len(yClear), len(farmidClear), arrayfileClear.shape)
        
    else:
        print(f'Saving without the need to filter out NA data.')
        # Saving:

        print(f'Saving target y to {fp1}.')
        utils.save_intensities(fp1, idsdf['y'])
        
        print(f'Saving farmID to {fp2}.')
        utils.save_intensities(fp2, idsdf['farmID'])
        
        print(f'Saving arrayfiles into {fp3}.')
        np.savez_compressed(fp3, arrayfile)
        
# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputpath:
            raise Exception('Missing farmID or target filepath argument. Try --help .')

        print(f'\n08-makeTarget.py')
        print(f'\nStacked data in: {args.inputpath}')

        # directory for results:
        out_dir_path = os.path.join(str(Path(args.inputpath).parents[0]),  'dataStack_ard')
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)

        print("\nFrom farmID extract crop yields to make target set y...")
        
        if args.year == None:
            filenames = glob.glob(args.inputpath + 'array*.npz')    
        else:
            filenames = glob.glob(args.inputpath + 'array*' + args.year + '.npz')
            
        print(filenames)
        if filenames:
            for fp in filenames:
                print(fp)
                makeTarget(fp, out_dir_path)
        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write out statistics. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputpath',
                        help='Path to array filepath.',
                        type=str)
    parser.add_argument('-y', '--year',
                        default = None,
                        help='Optionally year. Takes all array file matching that year.',
                        type=str)

    parser.add_argument('--debug',
                        help='Verbose output for debugging.',
                        action='store_true')

    args = parser.parse_args()
    main(args)
