"""
2023-09-11 MY

Calculate RMSEs of predictions and true yields. Take the mean. Make a regression between true yield deviation from 10 year mean and RSME.

RUN:

python 18-RMSE-deviationMean-regression.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack_ard/y_1310-2021.pkl \
-p /scratch/project_2006665/cropyield2023/training/cloudy/predictions/2023-08-22/1310-2018-2019-2020-2022/TCNtest/TCNtestPreds.pkl \
-j tenYearYieldMeans.csv

WHERE:
i: true yields
p: predictions
j: 10 year mean of true yields

"""
import numpy as np
import pickle
import pandas as pd
import seaborn as sns
import os
import re
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt


import argparse
import textwrap

def _load_intensities(filename):
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data

def _parse_setti_from_ypath(p: str): # farmID
    vilja = re.match('.*y_([0-9].*).pkl', p)
    return vilja[1] if vilja else None



# MAIN:
def main(args):
    try:
        if not args.inputfile :
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n18-RMSE-deviationMean-regression.py')

        ytrue = _load_intensities(args.inputfile)
        print(ytrue.shape)

        preds = _load_intensities(args.predsfile)
        preds.shape

        #df = pd.DataFrame(data = preds[:,-1,:], columns = ['Predicted yield'])
        #df['True yield'] = ytrue

        #setti = _parse_setti_from_ypath(args.inputfile)

        #residuals = np.subtract(preds[:,-1,:].squeeze(), ytrue)
        #rmse = np.sqrt(np.square(residuals).mean())
        #R2 = r2_score(ytrue, preds[:,-1,:].squeeze())

        #ax = sns.histplot(data=df)
        #ax.set_xlabel('Yield (kg/ha)')
        #ax.set_title(setti)

        #ax.text(6000, 55, f'RMSE: {round(rmse)}kg', 
        #       fontsize = 12,          # Size
        #       color = "red",          # Color
        #       ha = "center", # Horizontal alignment
        #       va = "center") # Vertical alignment 

        #ax.text(6000, 75, f'$R^2$: {round(R2, 2)}', 
        #       fontsize = 12,          # Size
        #       color = "red",          # Color
        #       ha = "center", # Horizontal alignment
        #       va = "center") # Vertical alignment 
        
        out_dir_path = os.path.join(str(Path(args.inputpath).parents[2]),  'analysis')
        Path(out_dir_path).mkdir(parents=True, exist_ok=True)

        outputfile = os.path.join(out_dir_path, 'RMSE-meanYield' + setti + '-300dpi.png')
        print(f'Output in {outputfile}.')
        #plt.savefig(outputfile, format='png', dpi=300)
        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write out statistics. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputfile',
                        help='Filepath of true yields.',
                        type=str)
    parser.add_argument('-p', '--predsfile',
                        help='Filepath of the predicted yields.',
                        type=str)   

    args = parser.parse_args()
    main(args)
