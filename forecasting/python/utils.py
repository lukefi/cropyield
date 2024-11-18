"""
2021-09-03 MY 

Utility functions for ML-modelling

"""

import numpy as np
import pickle
import pandas as pd
import os.path
import re


def _load_intensities(filename):
    with open(filename, "rb") as f:
        #data = pickle.load(f)
        data = pd.read_pickle(f)
    return data

def load_npintensities(fp):
    xtrain = np.load(fp)['arr_0']
    #print(f'Shape of xtrain: {xtrain.shape}')
    return xtrain

def save_intensities(filename, arrayvalues):
    with open(filename, 'wb+') as outputfile:
        pickle.dump(arrayvalues, outputfile)
        
def _l1_normalization(a):
    return (np.nan_to_num(a/a.sum()))

def _linearScaling_normalization(a):
    normalized = (a-min(a))/(max(a)-min(a))
    return (np.nan_to_num(normalized))
    
def normalise3D(xtrain, normalizer):
    
    xtrain4d = xtrain.reshape(xtrain.shape[0], xtrain.shape[1], 10, -1)    

    if normalizer == "median":
        print(f"Shape of 3D set: {xtrain.shape}")
        normalized = np.apply_along_axis(_divide, 2, xtrain)
    # Normalisoidaan 4. ulottovuus eli 3rd axis:
    elif normalizer == "linear":
        print(f"Normalizing ({normalizer}). First reshaping 3D set {xtrain.shape} into 4D set {xtrain4d.shape}.")
        normalized = np.apply_along_axis(_linearScaling_normalization, 3, xtrain4d)
    else:
        print(f"Normalizing ({normalizer}). First reshaping 3D set {xtrain.shape} into 4D set {xtrain4d.shape}.")
        normalized = np.apply_along_axis(_l1_normalization, 3, xtrain4d)
    return normalized

def parse_xpath(p: str): 
    # parse croptype(s) and year(s), i.e. the name of the data set
    vilja2 = re.match('.*array_([0-9].*).npz', p)[1]
    if '1310-1320-2024' in vilja2:
        vilja2 = '1300-2024'    
    return vilja2 if vilja2 else None

def _parse_setti_from_farmIDpath(p: str): # farmID
    vilja = re.match('.*farmID_([0-9].*).pkl', p)
    return vilja[1] if vilja else None

def _parse_setti_from_predsPath(p: str): # for munging predictions
    vilja = p.split('/')[-2]
    return vilja if vilja else None

def readTarget(filename):
    tail = parse_xpath(filename)
    print(tail)
    fp = 'y_' + tail + '.pkl'
    y = _load_intensities(os.path.join(os.path.dirname(filename), fp)).astype('float')
    return y

def readTargetID(filename):
    tail = parse_xpath(filename)
    print(tail)
    fp = 'farmID_' + tail + '.pkl'
    y = _load_intensities(os.path.join(os.path.dirname(filename), fp))
    return y

def split_data(xtrain, ytrain):
    # Reserve 20% of samples for validation
    splitting = int(len(ytrain)*.2)
    x_val = xtrain[-splitting:]
    y_val = ytrain[-splitting:]
    x_train = xtrain[:-splitting]
    y_train = ytrain[:-splitting]
    return x_train, y_train, x_val, y_val


def _divide(a):
    return (np.nan_to_num(a/10000))
