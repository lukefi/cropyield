"""
MY 2021-10-06 combine RMSE results 
2023-07-31 modified for current state: cloudy
2023-09-13 MTP varten

RUN:
python 11-combineResults.py -i /Users/myliheik/Documents/myCROPYIELD/scratch/project_2006665/cropyield2023/training/cloudy/predictions/2023-08-22

"""

import glob
import pandas as pd
import os.path
from pathlib import Path


import argparse
import textwrap



# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputpath:
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n11-combineResults.py')
        print(f'\nPrediction results in: {args.inputpath}')


        print(f'\nRead all parametersRMSE.csv files...')

        df = pd.concat([pd.read_csv(f, header=None) for f in glob.iglob(args.inputpath + '/*/*/parametersRMSE.csv')])
        


        df[['Crop', 'Year']] = df[0].str.split('-', 1, expand = True)
        #print(df)        
        df3 = df.rename(columns = {1: 'modelname', 2: 'epochs', 3: 'batchsize', 4: 'optimizeri', 5: 'lera', 6: 'epsiloni', 7: 'RMSE', 8: 'RMSE-%', 
                              9: 'ytestmean', 10: 'len(ytest)', 11: 'ytrainmean', 12: 'len(ytrain)', 13: 'ypredmean', 14: 
                                   'ytestsd', 15: 'ytrainsd', 16: 'ypredsd', 17: 'normalizer'})
        
        
        if 'combo' in args.inputpath:
            df3['setID'] = df3['setID'] + 'combo'
        if 'rank' in args.inputpath:
            df3['setID'] = df3['setID'] + 'rank'
                
        if 'cloudless' in args.inputpath:
            df3['mask'] = 'cloudless'
        else:
            df3['mask'] = 'cloudy'
            
            
        

        print(df3)
        print(df3[['RMSE', 'RMSE-%','Year']].groupby('Year').describe())

        print(df3[['RMSE', 'RMSE-%','Crop']].groupby('Crop').describe())

        #df3.to_latex(os.path.join(args.inputpath, 'combinedResults.tex'), index=False)
        fp = os.path.join(args.inputpath, 'combinedResults.csv')
        print(f'\nWriting output into {fp}')
        df3.to_csv(fp, index=False)
      
        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write out statistics. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputpath',
                        help='Upper filepath of RMSE results (date).',
                        type=str)

    args = parser.parse_args()
    main(args)

