"""
2021-09-01 MY added normalization
2021-10-05 MY added naming of testing results directory
2021-11-30 added TCN
2022-06-02 added training only option
2024-04-12 introduced MLflow

RUN:

Without testing set (makes train/validation split automatically):
python 09-runTCN.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack_ard/array_1110-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1

With testing set (region or separate year):
python 09-runTCN.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack_ard/array_1110-2018-2019-2020-2021.npz \
-j /scratch/project_2006665/cropyield2023/training/cloudy/dataStack/array_1110-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1

For training only and registering the model version (training the final model version):
python 09-runTCN.py -i /scratch/project_2006665/cropyield2023/training/cloudy/dataStack_ard/array_1400-2018-2019-2020-2021-2022.npz \
--epochs 200 --batchsize 128 --learningrate 0.001 --epsilon 0.1 -r

For prediction only:
python ../../forecasting/python/09-predict.py


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
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

import tensorflow as tf
from tcn import TCN, tcn_full_summary

# pip install keras-tcn --user
import matplotlib.pyplot as plt
import seaborn as sns

import mlflow
import mlflow.data
import mlflow.data.tensorflow_dataset
from mlflow import MlflowClient

# setup MLflow to use scratch for saving data
mlflow.set_tracking_uri("/scratch/project_2009889/mlruns")
client = MlflowClient()

t = time.localtime()
timeString  = time.strftime("%Y-%m-%d", t)

# FUNCTIONS:

def temporalConvolutionalNetworks(shape1, shape2, nbfilters, kernelsize, dilations):
    print("\nTraining TCN...")
    tcn_layer = TCN(input_shape=(None, shape2), nb_filters = nbfilters, padding = 'causal', kernel_size = kernelsize, 
                nb_stacks=1, dilations = dilations, 
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
    
    return model, tcn_layer.receptive_field

# get crop id for experiment organisation
def get_crop_id(file_path):
    filename = file_path.split('/')
    for part in filename:
        if 'array_' in part:
            number_part = part.replace('array_', '')
            numbers = number_part.split('-')
            if '-'.join(numbers[0:2]) == '1310-1320':
                crop_id = '1300'
            else:
                crop_id = numbers[0]
            return crop_id
    return None

# get params of a run by model version's alias
def get_params_by_alias(model_name, alias):
    model = client.get_model_version_by_alias(model_name, alias)
    run = mlflow.get_run(run_id=model.run_id)
    params = run.data.params
    return params
    

def runModel(model, modelname, Xtrain, ytrain, Xtest, 
             ytest, outputdir, epochs, batchsize, optimizeri, 
             lera, epsiloni, setID, normalizer, 
             mlflow_train_dataset, mlflow_val_dataset, crop_id, 
             registermodel, description, run_name, tags
            ):

    # Set the crop type as experiment name for ease managing and comparing runs
    experiment_name = f"{crop_id}" 
    experiment = mlflow.set_experiment(experiment_name)

    print("---")
    print(f"\nExperiment_id: {experiment.experiment_id}")
    print(f"Artifact Location: {experiment.artifact_location}")

    mlflow.tensorflow.autolog() # logs all parameters and metrics automatically

    with mlflow.start_run(description = ' '.join(description), tags = tags) as run:
        
        # Set name for the run
        if run_name:
            mlflow.set_tag("mlflow.runName", run_name)
            print(f"Run name: {run_name}")
          
        #mlflow.set_experiment_tags(tags)    
        #print(f"Tags: {experiment.tags}")          
        print("\n---")        
        
        # Save data fingerprint with the run 
        mlflow.log_input(mlflow_train_dataset,  context="training")
        if not registermodel:
            mlflow.log_input(mlflow_val_dataset, context="validation")
    
        if registermodel: # if r-flag is used: train model with parameters from "challenger" and create new model version
            params = get_params_by_alias(crop_id, 'challenger') # get parameters from "challenger" model
        
            # monitor validation progress
            early = EarlyStopping(monitor="val_loss", mode="min", patience=int(params.get('patience', 10)))
            callbacks_list = [early]
                
            if params.get('opt_name', optimizeri).lower() == 'adam':
                optimizer = Adam(learning_rate=float(params.get('opt_learning_rate', 0.01)),
                                 epsilon=float(params.get('opt_epsilon', 0.1)))
                model.compile(loss='mean_squared_error',
                              optimizer=optimizer,
                              metrics=['mse'])
        
            # and train the model with params from dict
            model.fit(Xtrain, ytrain,
                      epochs=int(params.get('epochs', 200)), 
                      batch_size=int(params.get('batch_size', 128)), 
                      verbose=0,
                      validation_split=float(params.get('validation_split', 0.75)),
                      callbacks=callbacks_list)
    
            # log and register new "champion" model version to MLflow
            artifact_path = f'{crop_id}_{timeString}'
            model_uri = f"runs:/{run.info.run_id}/{artifact_path}" # dir for model
            model_name = f"{crop_id}"
            alias = 'champion'
            print(f'\n\nLogging and registering the model to MLflow as {model_name}@{alias}\nArtifact path: {artifact_path}.')
            mlflow.tensorflow.log_model(
                model, 
                artifact_path=artifact_path)
            mv = mlflow.register_model(
                model_uri, 
                model_name)
            client.set_registered_model_alias(mv.name, 
                                              alias, 
                                              mv.version)
            print(f'Model registered with as {model_name}@{alias} version {mv.version}.')

        else: 
            # monitor validation progress
            early = EarlyStopping(monitor="val_loss", mode="min", patience=10)
            callbacks_list = [early]
                
            if optimizeri == 'adam':
                model.compile(loss='mean_squared_error',
                          optimizer=Adam(learning_rate=lera, epsilon=epsiloni),
                          metrics=['mse'])
        
            # and train the model
            history = model.fit(Xtrain, ytrain,
                                epochs=epochs, batch_size=batchsize,
                                verbose=0,
                                validation_split=0.20,
                                callbacks=callbacks_list)

            # RMSE
            mse = (mlflow.get_run(run.info.run_id)).data.metrics['mse'] # get the last mse value from MLflow
            rmse = float(np.sqrt(mse))
            mlflow.log_metric("t_rmse", rmse) # Log rmse manually to MLflow
            print("Training RMSE: ", rmse)
    
        
            """
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
            """
    
            # Evaluate the model on the validation or test data
            print('\nEvaluating the model on the test set:')
            results = model.evaluate(Xtest, ytest, batch_size = batchsize)
            print("\nTest set loss, test set acc:", results)
            
            rmse = math.sqrt(results[1])
            mlflow.log_metric("rmse", rmse) # Log rmse manually to MLflow
            print("RMSE: ", rmse)
            
            if modelname == "TCNtest": # We are doing some serious evaluations, e.g. leave-one-out
                test_predictions = model.predict(Xtest)       
                predfile = os.path.join(outputdir, modelname + 'Preds.pkl')
                print(f'Saving predictions on test set into {predfile}...\n')
                utils.save_intensities(predfile, test_predictions)

                rmse = round(math.sqrt(results[1]))
                rmsepros = round(rmse/np.mean(ytest), 2)
                # Mean
                ytestmean = round(np.mean(ytest))
                ytrainmean = round(np.mean(ytrain))
                ypredmean = round(np.mean(test_predictions[:, -1, 0]))
                # Std
                ytestsd = round(np.std(ytest))
                ytrainsd = round(np.std(ytrain))
                ypredsd = round(np.std(test_predictions[:, -1, 0]))
                

                print("RMSE-%: ", rmsepros*100, "%")
                
                outputdirmodel = os.path.join(outputdir, modelname)
                Path(outputdirmodel).mkdir(parents=True, exist_ok=True)
              
                csvfile = os.path.join(outputdirmodel, 'parametersRMSE.csv')
                print(f"\nWriting results to file {csvfile}")
                with open(csvfile, "a+") as f:
                    writer = csv.writer(f)
                    writer.writerow([setID, modelname, epochs, batchsize, optimizeri, lera, epsiloni, rmse, rmsepros*100, ytestmean, len(ytest), ytrainmean, len(ytrain), ypredmean, ytestsd, ytrainsd, ypredsd, normalizer])

            
            
        mlflow.end_run()
        print("\nAll done, check MLflow UI for results.")

# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputfile :
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n09-runTCN-mlflow.py')
        print(f'\nARD data set in: {args.inputfile}')
        
        if 'median' in args.inputfile:
            print('Median as a sole feature...')
            normalizer = 'median'
        else:   
            # EDIT:
            #normalizer = "linear" # or "L1"
            normalizer = "L1"
        
        # TCN parameters:
        nbfilters = args.nbfilters # default: 32
        kernelsize = args.kernelsize # default: 2
        dilations = args.dilations # default: [1, 2, 4, 8, 16]

        ############################# Preprocessing:        
        # read in array data:
        xtrain0 = utils.load_npintensities(args.inputfile)
        # normalize:
        xtrain = utils.normalise3D(xtrain0, normalizer)
        # read in target y:
        ytrain = utils.readTarget(args.inputfile)
        # jos ei anneta test set, niin tehdään split:       
        if not args.testfile:
            if not args.registermodel:
                print(f"\nSplitting {args.inputfile} into validation and training set:")
                xtrain, ytrain, xval, yval = utils.split_data(xtrain, ytrain)
                setID = utils.parse_xpath(args.inputfile)
            else:
                setID = utils.parse_xpath(args.inputfile)
        else:
            print(f"\nUsing {args.testfile} as a testing set:")
            xval0 = utils.load_npintensities(args.testfile)
            # normalize:
            xval = utils.normalise3D(xval0, normalizer)
            yval = utils.readTarget(args.testfile)
            setID = utils.parse_xpath(args.testfile) 
       
        if not args.testfile:
            print(f"\nNot going to save predictions...")
            basepath = args.inputfile.split('/')[:-2]
            out_dir_results = os.path.join(os.path.sep, *basepath, 'predictions', timeString, utils.parse_xpath(args.inputfile))
            #Path(out_dir_results).mkdir(parents=True, exist_ok=True)
            #print(f"\nRunning training but why would I save validation set predictions into {out_dir_results}?")

        else:
            basepath = args.testfile.split('/')[:-2]
            out_dir_results = os.path.join(os.path.sep, *basepath, 'predictions', timeString, utils.parse_xpath(args.inputfile))
            Path(out_dir_results).mkdir(parents=True, exist_ok=True)    
            print(f"\nRunning training and saving test set predictions into {out_dir_results}.")
    
        # this needs 3D:
        m,n = xtrain.shape[:2]
        xtrain3d = xtrain.reshape(m,n,-1) 
        if not args.registermodel:
            m,n = xval.shape[:2]
            xval3d = xval.reshape(m,n,-1) 
        else:
            xval3d = None
            yval = None

        # Convert data to correct form, for saving data fingerprint to MLflow
        ytrain_tensor = tf.convert_to_tensor(ytrain.values)
        yval_tensor = tf.convert_to_tensor(yval.values) if yval is not None else None
        
        train_dataset = tf.data.Dataset.from_tensor_slices((xtrain3d, ytrain_tensor))
        val_dataset = tf.data.Dataset.from_tensor_slices((xval3d, yval_tensor)) if not args.registermodel else None

        mlflow_train_dataset = mlflow.data.tensorflow_dataset.from_tensorflow(
            features=train_dataset,
            source=args.inputfile)
        
        mlflow_val_dataset = mlflow.data.tensorflow_dataset.from_tensorflow(
            features=val_dataset,
            source=args.inputfile) if val_dataset is not None else None

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
        
        model, receptive_field = temporalConvolutionalNetworks(xtrain3d.shape[1], xtrain3d.shape[2], nbfilters, kernelsize, dilations)

        tags = {
            "nb_filters": nbfilters,
            "kernel_size": kernelsize,
            "dilations": ', '.join(map(str, dilations)),
            "receptive_field": receptive_field
        }        
        
        if normalizer == 'median':
            modelname = 'TCNmedian'
        else:
            if not args.testfile:
                modelname = 'TCN'
            else:
                modelname = 'TCNtest'
        
        crop_id = get_crop_id(args.inputfile)
       

        runModel(model, modelname, xtrain3d, ytrain, xval3d, yval, 
                 out_dir_results, args.epochs, args.batchsize, args.optimizer, 
                 args.learningrate, args.epsilon, setID, normalizer,  
                 mlflow_train_dataset, mlflow_val_dataset, crop_id, 
                 args.registermodel, 
                 args.description,
                 args.run_name, tags
                )
        
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
                        type=float, default = 0.001) 
    parser.add_argument('-p', '--epsilon',
                        help='A small constant for numerical stability (defaults to 1e-07).',
                        type=float, default = 0.0000001) 
    parser.add_argument('-f', '--nbfilters',
                        help='TCN filters (defaults to 32).',
                        type=int, default = 32)     
    parser.add_argument('-k', '--kernelsize',
                        help='TCN kernel size (defaults to 2).',
                        type=int, default = 2)  
    parser.add_argument('-s', '--dilations', action='store', dest='dilations',
                        help='TCN dilations (defaults to 1, 2, 4, 8, 16).',
                        type=int, nargs='*', default = [1, 2, 4, 8, 16])  
    
    parser.add_argument('-r', '--registermodel',
                        help='Train model and register new version to MLflow',
                        action='store_true')
    parser.add_argument('-d', '--description', action='store', dest='description',
                        help='Description for the run.',
                        type=str, nargs='*', default=None)
    parser.add_argument('-n', '--run_name',
                        help='Name for the run.', default = None,
                        type=str)    
    parser.add_argument('--debug',
                        help='Verbose output for debugging.',                        
                        action='store_true')
    args = parser.parse_args()
    main(args)
