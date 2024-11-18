"""
2021-09-01 MY added normalization
2021-10-05 MY added naming of testing results directory
2021-11-30 added TCN
2022-06-02 added training only option

RUN:

Without testing set (makes train/validation split automatically):
python 09-runTCN.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack_ard/array_1110-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1

With testing set (region or separate year):
python 09-runTCN.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack_ard/array_1110-2018-2019-2020-2021.npz \
-j /scratch/project_2006665/cropyield2023/training/cloudy/dataStack/array_1110-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1

For training only and saving the model:
python 09-runTCN.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack_ard/array_1400-2018-2019-2020-2021-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -t

For prediction only:
python 09-predict.py


NOTE: if you test with a separate year, be sure that training set excludes that year!


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

def temporalConvolutionalNetworks(shape1, shape2):
    print("\nTraining TCN...")
    tcn_layer = TCN(input_shape=(None, shape2), nb_filters = 32, padding = 'causal', kernel_size = 2, 
                nb_stacks=1, dilations = [1, 2, 4, 8, 16], 
                return_sequences=True
               )
    # The receptive field tells you how far the model can see in terms of timesteps.
    print('Receptive field size =', tcn_layer.receptive_field)

    model = Sequential([
        tcn_layer,
        Dense(1)
        ])
    

    # Model summary:
    print('\nNetwork architecture:')
    print(model.summary())
    #print(tcn_full_summary(model))
    
    return model
    

def runModel(model, modelname, Xtrain, ytrain, Xtest, ytest, outputdir, epochs, batchsize, optimizeri, lera, epsiloni, setID, normalizer, trainonly):

    # monitor validation progress
    early = EarlyStopping(monitor = "val_loss", mode = "min", patience = 10)
    callbacks_list = [early]
    
    if optimizeri == 'adam':
        model.compile(loss = 'mean_squared_error',
                  optimizer = Adam(learning_rate=lera, epsilon = epsiloni),
                  metrics = ['mse'])

    # and train the model
    history = model.fit(Xtrain, ytrain,
        epochs=epochs,  batch_size=batchsize, verbose=0,
        validation_split = 0.20,
        callbacks = callbacks_list)

    outputdirmodel = os.path.join(outputdir, modelname)
    Path(outputdirmodel).mkdir(parents=True, exist_ok=True)
    fname = os.path.join(outputdirmodel, 'networkArchitectureFullDataset.pdf')
    #print(f'\nSaving network architecture into file {fname}')
    #plot_model(model, to_file=fname, show_shapes=True, rankdir='LR')

    # Saving the model:
    print(f'\nSaving the model into {outputdirmodel}')
    model.save(outputdirmodel)

    # Saving training history into file...
    fname = os.path.join(outputdirmodel, 'trainingHistoryFulldata.pdf')
    print(f'\nSaving training history into file {fname}...\n')
    fig = plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='val')
    plt.legend()
    plt.savefig(fname, dpi=300)

    if not trainonly:
        test_predictions = model.predict(Xtest)

        x = np.arange(0, 8000, 100)
        y = x
        fname = os.path.join(outputdirmodel, setID + '-' + modelname + '-scatterPlot.pdf')
        ax = sns.scatterplot(x=ytest, y=test_predictions[:,-1,0])
        ax.set(xlabel='y', ylabel='y_hat', title=setID)
        # control x and y limits
        plt.ylim(0, 8000)
        plt.xlim(0, 8000)
        ax.plot(y, x)
        # Saving scatter plot into file...
        plt.savefig(fname, dpi=300)



        # Evaluate the model on the test data
        print('\nEvaluating the model on the test set:')
        results = model.evaluate(Xtest, ytest, batch_size=batchsize)
        print("\nTest set loss, test set acc:", results)
        rmse = math.sqrt(results[1])
        print("RMSE: ", rmse)
        csvfile = os.path.join(outputdirmodel, 'parametersRMSE.csv')
        print(f"\nWriting results to file {csvfile}.")
        with open(csvfile, "a+") as f:
            writer = csv.writer(f)
            writer.writerow([setID, modelname, epochs, batchsize, optimizeri, lera, epsiloni, rmse, normalizer])


        dfPreds = pd.DataFrame(test_predictions[:, -1, 0])
        dfPreds.columns = ['farmfinal']

        # starts 10.5. eli DOY 130, starts 4.5. eli DOY 124
        # Predictions to compare with forecasts: 15.6. eli DOY 166, that is pythonic 165. DOYID 17
        # and 15.7. eli DOY 196. DOYID 28
        # and 15.8. eli DOY 227. DOYID 39.
        # and the last DOY 243 -> the final state. DOYID 48.

        # in this case using doys (130-243) (43, 73, 104):
        june = 43
        july = 73
        august = 104
        #June:
        #rmse2 = np.sqrt(np.square(np.subtract(test_predictions[:,-1].flatten(), ytest[170:171])).mean())
        dfPreds['farm43'] = test_predictions[:, june, 0]

        #July:
        dfPreds['farm73'] = test_predictions[:, july, 0]#.flatten()

        #August:
        dfPreds['farm104'] = test_predictions[:, august, 0]#.flatten()

        dfPredsFinal= dfPreds#.iloc[:,[166-129, 196-129, 227-129, dfPreds.shape[1]-1]]


        print(dfPredsFinal.describe())
        print(stats.describe(test_predictions[:,-1,0]))
        print(stats.describe(ytest))
        predfile = os.path.join(outputdirmodel, modelname + 'Preds.pkl')
        print(f'Saving predictions on test set into {predfile}...\n')
        utils.save_intensities(predfile, dfPredsFinal[['farm43','farm73', 'farm104', 'farmfinal']])
        
    else:
        print(f'Model saved, all done.')

# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputfile :
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n09-runTCN.py')
        print(f'\nARD data set in: {args.inputfile}')
        
        if 'median' in args.inputfile:
            print('Median as a sole feature...')
            normalizer = 'median'
        else:   
            # EDIT:
            #normalizer = "linear" # or "L1"
            normalizer = "L1"

        ############################# Preprocessing:        
        # read in array data:
        xtrain0 = utils.load_npintensities(args.inputfile)
        # normalize:
        xtrain = utils.normalise3D(xtrain0, normalizer)
        # read in target y:
        ytrain = utils.readTarget(args.inputfile)
        # jos ei anneta test set, niin tehdään split:       
        if not args.testfile:
            if not args.trainonly:
                print(f"\nSplitting {args.inputfile} into validation and training set:")
                xtrain, ytrain, xval, yval = utils.split_data(xtrain, ytrain)
                setID = utils.parse_xpath(args.inputfile)
            else:
                setID = utils.parse_xpath(args.inputfile)

        else:
            xval0 = utils.load_npintensities(args.testfile)
            # normalize:
            xval = utils.normalise3D(xval0, normalizer)
            yval = utils.readTarget(args.testfile)
            setID = utils.parse_xpath(args.testfile) 
        
        if not args.testfile:
            basepath = args.inputfile.split('/')[:-2]
            out_dir_results = os.path.join(os.path.sep, *basepath, 'predictions', timeString, utils.parse_xpath(args.inputfile))
            Path(out_dir_results).mkdir(parents=True, exist_ok=True)
        else:
            basepath = args.testfile.split('/')[:-2]
            out_dir_results = os.path.join(os.path.sep, *basepath, 'predictions', timeString, utils.parse_xpath(args.inputfile))
            Path(out_dir_results).mkdir(parents=True, exist_ok=True)
        
        
        print(f"\nRunning training and saving test set predictions into {out_dir_results}.")
        # this needs 3D:
        m,n = xtrain.shape[:2]
        xtrain3d = xtrain.reshape(m,n,-1) 
        if not args.trainonly:
            m,n = xval.shape[:2]
            xval3d = xval.reshape(m,n,-1) 
        else:
            xval3d = None
            yval = None

        # forget zero-padding for TCN:
        #if xval3d.shape[1] < xtrain3d.shape[1]:
        #    doysToAdd = xtrain3d.shape[1] - xval3d.shape[1]
        #    print(f"Shape of testing set differs from training set. We need to pad it with {doysToAdd} DOYs.")
        #    b = np.zeros( (xval3d.shape[0],doysToAdd,xval3d.shape[2]) )
        #    xval3d = np.column_stack((xval3d,b))
        #    print(f'New shape of padded xval3d is {xval3d.shape}.')   
            
        #if xtrain3d.shape[1] < xval3d.shape[1]:
        #    doysToAdd = xval3d.shape[1] - xtrain3d.shape[1]
        #    print(f"Shape of training set differs from testing set. We need to pad it with {doysToAdd} DOYs.")
        #    b = np.zeros( (xtrain3d.shape[0],doysToAdd,xtrain3d.shape[2]) )
        #    xtrain3d = np.column_stack((xtrain3d,b))
        #    print(f'New shape of padded xtrain3d is {xtrain3d.shape}.')   

        ##################################### Models:    
        # model topology:
        
        model = temporalConvolutionalNetworks(xtrain3d.shape[1], xtrain3d.shape[2])
        if normalizer == 'median':
            modelname = 'TCNmedian'
        else:
            if not args.testfile:
                modelname = 'TCN'
            else:
                modelname = 'TCNtest'
                
        
        runModel(model, modelname, xtrain3d, ytrain, xval3d, yval, out_dir_results, args.epochs, args.batchsize, args.optimizer, args.learningrate, args.epsilon, setID, normalizer, args.trainonly)


        
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
    parser.add_argument('-j', '--testfile',
                        help='Filepath of the testing set (optional).',
                        type=str)   
    parser.add_argument('-t', '--trainonly',
                        help = 'Only train the model and save',
                        action = 'store_true')
    parser.add_argument('-e', '--epochs',
                        help='An epoch is an iteration over the entire x and y data provided (default 20).',
                        type=int, default = 20)      
    parser.add_argument('-b', '--batchsize',
                        help='Number of samples per gradient update (default 32).',
                        type=int, default = 32)  
    parser.add_argument('-o', '--optimizer',
                        help='Optimizer (default adam).',
                        type=str, default = 'adam') 
    parser.add_argument('-l', '--learningrate',
                        help='Learning rate (defaults to 0.001).',
                        type=float, default = '0.001') 
    parser.add_argument('-p', '--epsilon',
                        help='A small constant for numerical stability (defaults to 1e-07).',
                        type=float, default = '0.0000001') 
    parser.add_argument('--debug',
                        help='Verbose output for debugging.',
                        action='store_true')

    args = parser.parse_args()
    main(args)
