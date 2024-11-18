"""
2022-06-02 MY: for prediction only, uses saved TCN model

RUN:

python 09-predict.py -i /scratch/project_2001253/cropyield2022/cloudy/dataStack_ard/array_1120-2018.npz \
-m /scratch/project_2001253/cropyield2022/cloudy/predictions/2022-06-02/1110-2018-2019-2020-2021/TCN


"""
import glob
import pandas as pd
import numpy as np
import os.path
from pathlib import Path
import argparse
import textwrap
import math
import time
import csv
from scipy import stats
import utils

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from tensorflow.keras.models import Sequential, save_model, load_model
from tensorflow.keras.layers import Dense, Dropout, SimpleRNN, LSTM
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.utils import plot_model
from tensorflow.keras.optimizers import Adam

from tcn import TCN, tcn_full_summary

# pip install keras-tcn --user
import matplotlib.pyplot as plt
import seaborn as sns

t = time.localtime()
timeString  = time.strftime("%Y-%m-%d", t)

# FUNCTIONS:
 
def runPredictions(modelpath, modelname, Xtest, outputdir, setID, normalizer):

    model = load_model(modelpath)

    test_predictions = model.predict(Xtest)
    
    print(stats.describe(test_predictions[:,-1,0]))

    predfile = os.path.join(outputdir, modelname + 'Preds.pkl')
    print(f'Saving predictions on test set into {predfile}...\n')
    utils.save_intensities(predfile, test_predictions)
        
# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputfile :
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n09-predict.py')
        print(f'\nNew unseen data set in: {args.inputfile}')
        
        if 'median' in args.inputfile:
            print('Median as a sole feature...')
            normalizer = 'median'
        else:   
            # EDIT:
            #normalizer = "linear" # or "L1"
            normalizer = "L1"

        ############################# Preprocessing:        
        # read in array data:
        xtest0 = utils.load_npintensities(args.inputfile)
        # normalize:
        xtest = utils.normalise3D(xtest0, normalizer)
        
        # model needs 3D:
        m,n = xtest.shape[:2]
        xtest3d = xtest.reshape(m,n,-1) 

        setID = utils.parse_xpath(args.inputfile)

        basepath = args.inputfile.split('/')[:-2]
        out_dir_results = os.path.join(os.path.sep, *basepath, 'predictions', timeString, utils.parse_xpath(args.inputfile))
        Path(out_dir_results).mkdir(parents=True, exist_ok=True)
        
        
        print(f"\nSaving test set predictions into {out_dir_results}.")
        
        if normalizer == 'median':
            modelname = 'TCNmedian'
        else:
            modelname = 'TCN'

                
                
        runPredictions(args.modelpath, modelname, xtest3d, out_dir_results, setID, normalizer)        

        print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write out statistics. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputfile',
                        help='Filepath of array intensities (training set).',
                        type=str)
    parser.add_argument('-m', '--modelpath',
                        help='Filepath to the model.',
                        type=str)   
    parser.add_argument('--debug',
                        help='Verbose output for debugging.',
                        action='store_true')

    args = parser.parse_args()
    main(args)
