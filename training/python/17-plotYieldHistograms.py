"""
2023-09-08 MY

Calculate histograms of predictions and true yields.

RUN:

python 17-plotYieldHistograms.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack_ard/y_1310-2021.pkl \
-p /scratch/project_2006665/cropyield2023/training/cloudy/predictions/2023-08-22/1310-2018-2019-2020-2022/TCNtest/TCNtestPreds.pkl

WHERE:
i: true yields
p: predictions


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

        print(f'\n17-plotYieldHistograms.py')

        ytrue = _load_intensities(args.inputfile)
        print(ytrue.shape)

        preds = _load_intensities(args.predsfile)
        preds.shape

        df = pd.DataFrame(data = preds[:,-1,:], columns = ['Predicted yield'])
        df['True yield'] = ytrue

        setti = _parse_setti_from_ypath(args.inputfile)

        residuals = np.subtract(preds[:,-1,:].squeeze(), ytrue)
        rmse = np.sqrt(np.square(residuals).mean())
        R2 = r2_score(ytrue, preds[:,-1,:].squeeze())

        ax = sns.histplot(data=df)
        ax.set_xlabel('Yield (kg/ha)')
        ax.set_title(setti)

        ax.text(6000, 55, f'RMSE: {round(rmse)}kg', 
               fontsize = 12,          # Size
               color = "red",          # Color
               ha = "center", # Horizontal alignment
               va = "center") # Vertical alignment 

        ax.text(6000, 75, f'$R^2$: {round(R2, 2)}', 
               fontsize = 12,          # Size
               color = "red",          # Color
               ha = "center", # Horizontal alignment
               va = "center") # Vertical alignment 

        outputfile = os.path.join('/scratch/project_2006665/cropyield2023/training/img/histograms-preds-true-yield-' + setti + '-300dpi.png')
        print(f'Histogram plot in {outputfile}.')
        plt.savefig(outputfile, format='png', dpi=300)
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
