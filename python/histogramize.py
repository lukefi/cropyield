
"""
preparing for ML:
input array csvs from main program, each line representing one field, first number being ID of the field
output similar csv with each line representing one field, first number being ID of field, followed by x = bins numbers representing histogram values
"""




import os
import numpy as np
import sys
import csv


datadir = sys.argv[1]
bins = int(sys.argv[2])
perc = float(sys.argv[3])

def to_csv(csvfile, myarray):
    
    csvfile = csvfile.replace('array_','histogram_')
    with open(csvfile, "w") as f:
        writer = csv.writer(f)
        writer.writerows(myarray)

def remove_extremes(myarray, perc):

        #sort
        sorted = np.sort(myarray)
        #length
        length = len(sorted)
        # length * percentage to cut off
        low = round(length * perc)
        # 1 - e to cut upper and lower
        high = length - low
        #print(low,high)

        shortarray = myarray[int(low):int(high)]

        return shortarray

def make_histogram(inarray,perc, bins):

    shortarray = remove_extremes(inarray, perc)

    hist = np.histogram(shortarray, bins = bins) # a tuple
    #histval = hist[0] # an array of the histogram values
    #histdel = hist[1] # an array of the bin delimiters

    return hist[0]



for arrayfile in os.listdir(datadir):
    if arrayfile.endswith('.csv') and arrayfile.startswith('array_'):
        histlist = []
        arraypath = os.path.join(datadir,arrayfile)
        #print(arraypath)
        with open(arraypath, "r") as f:
            reader = csv.reader(f)
            for line in reader:
                myid = [line[0]]
                line =[int(elem) for elem in line if not '_' in elem]
                #print(line)
                hist = make_histogram(line, perc, bins)
                #print(hist)
                
                #print(myid)
                myid.extend(hist)
                #print(myid)
                hist2 = myid
                #print(hist)
                histlist.append(hist2)
                #print(arraypath)
                #print(histlist)
            
            to_csv(arraypath,histlist)
        


