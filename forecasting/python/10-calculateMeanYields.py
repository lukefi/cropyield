"""
MY 
2024-06-14 
2024-09-06 added date to filename (a3) and now saves all season data into .csv as well

RUN:
python 10-calculateMeanYields.py -i /scratch/project_2009889/cropyield2024/forecasting/cloudy/predictions/2024-06-20 -b satoennusteet2024

"""

import glob
import pandas as pd
import os.path
from pathlib import Path
import utils

import argparse
import textwrap

import datetime
import boto3


# HERE STARTS MAIN:

def main(args):
    try:
        if not args.inputpath:
            raise Exception('Missing input filepath argument. Try --help .')

        print(f'\n10-calculateMeanYields.py')
        print(f'\nPrediction results in: {args.inputpath}')
        print(f'\nForecasts saved in s3 bucket: {args.bucketname}')

        s3_resource = boto3.resource('s3', endpoint_url='https://a3s.fi')
        my_bucketname = args.bucketname
        
        fp = args.inputpath
        reportfile = os.path.join(fp, 'yields.csv')
        reportfile2 = os.path.join(fp, 'keskisadot.csv')

        # Date:
        pvm0 = args.inputpath
        pvm00 = pvm0.split('/')[-1]
        
        
        try:
            os.remove(reportfile)
        except OSError:
            pass    
        
        try:
            os.remove(reportfile2)
        except OSError:
            pass    
        
        print(f'\nRead all prediction files and report national mean yields to\n{reportfile}...')

        fps = glob.iglob(args.inputpath + '/*/TCNPreds.pkl')
        for filename in fps:
            print(filename)
            
            
            basedir = Path(filename).parents[3]
            setti = utils._parse_setti_from_predsPath(filename)
            cropid = setti.split('-')[:-1][0]
            year = setti.split('-')[-1]
            if setti == '1300-' + year:
                setti = '1310-1320-' + year
            parcelfile = os.path.join(basedir, 'dataStack', 'parcelID_' + setti + '.pkl')
            parcels = pd.DataFrame(utils._load_intensities(parcelfile))
            parcels2 = parcels[0].str.split('_', expand = True) # '2024_16277895_1320_2_529_141'
            parcels2.rename(columns = {0: 'Year', 1: 'parcelID', 2: 'Croptype', 3: 'Maakunta', 4: 'Municipality', 5: 'Area'}, inplace = True)
            
            array = utils._load_intensities(filename)
            df = pd.DataFrame(array.squeeze())
            try:
                if not df.shape[0] == parcels.shape[0]:
                        raise Exception(f"Preds and parcels don't match! There are {parcels.shape[0]} parcels and {df.shape[0]}")
                # Merge preds and parcels:                        
                dfall = pd.concat([parcels2, df], axis = 1)
                dfall['Area'] = dfall['Area'].astype(float) / 100

                
                # Save data in csv for further analysis:
                
                # dictionary:
                doyDict = {0: 122, 1: 123, 2: 124, 3: 125, 4: 126, 5: 127, 6: 128, 7: 129, 8: 130, 9: 131, 10: 132, 11: 133, 
           12: 134, 13: 135, 14: 136, 15: 137, 16: 138, 17: 139, 18: 140, 19: 141, 20: 142, 21: 143, 22: 144, 
           23: 145, 24: 146, 25: 147, 26: 148, 27: 149, 28: 150, 29: 151, 30: 152, 31: 153, 32: 154, 33: 155, 
           34: 156, 35: 157, 36: 158, 37: 159, 38: 160, 39: 161, 40: 162, 41: 163, 42: 164, 43: 165, 44: 166, 
           45: 167, 46: 168, 47: 169, 48: 170, 49: 171, 50: 172, 51: 173, 52: 174, 53: 175, 54: 176, 55: 177, 
           56: 178, 57: 179, 58: 180, 59: 181, 60: 182, 61: 183, 62: 184, 63: 185, 64: 186, 65: 187, 66: 188, 
           67: 189, 68: 190, 69: 191, 70: 192, 71: 193, 72: 194, 73: 195, 74: 196, 75: 197, 76: 198, 77: 199, 
           78: 200, 79: 201, 80: 202, 81: 203, 82: 204, 83: 205, 84: 206, 85: 207, 86: 208, 87: 209, 88: 210, 
           89: 211, 90: 212, 91: 213, 92: 214, 93: 216, 94: 217, 95: 218, 96: 219, 97: 220, 98: 221, 99: 222, 
           100: 223, 101: 224, 102: 225, 103: 226, 104: 227, 105: 228, 106: 229, 107: 230, 108: 231, 109: 232, 
           110: 233, 111: 234, 112: 235, 113: 236, 114: 237, 115: 238, 116: 239, 117: 240, 118: 241, 119: 242, 
           120: 243, 121: 245}
                
                # Take dates as order number and change to DOYs:
                doys = [*map(doyDict.get, dfall.columns[6:].values)]
                #print(dfall.columns[6:].values)
                # change DOYs to dates:
                doys2 = [datetime.datetime(2024, 1, 1) + datetime.timedelta(DOY - 1) for DOY in doys] 
                doys3 = [k.strftime('%Y-%m-%d') for k in doys2]
                days_dict = dict(zip(dfall.columns[6:].values, doys3))
                dfallCSV = dfall.rename(columns = days_dict)
                
                outputfile = os.path.join(os.path.dirname(filename), cropid + '-' + 'allPreds.csv')
                print(f'Saving all data into {outputfile}')
                round(dfallCSV, 0).to_csv(outputfile, index = False)
                
                # boto3:               
                boto3file6 = cropid + '-' + 'allPreds.csv'
                print(f'Saving all data into Allas {boto3file6}')
                s3_resource.Object(my_bucketname, boto3file6).upload_file(outputfile, ExtraArgs={'ACL':'public-read'})
                
                
                # for weighted mean:
                dfall.rename(columns = days_dict, inplace = True)
                dfall['tmp_weighted_yield'] = dfall.iloc[:,-1] * dfall['Area']
                
                # koko maan ka:
                nationalMean = dfall['tmp_weighted_yield'].sum() / dfall['Area'].sum()
                
                print('\n--------')
                print(f'\nNational weighted mean yield for {cropid} in {year}: {nationalMean.astype(int)} kg/ha')                     
                
                print('\n--------')    
                
                f = open(reportfile, "a")
                #f.write(f'\nNational mean yield for {cropid} in {year}: {dfall.iloc[:,-1].mean().astype(int)} kg/ha\n')
                f.write(f'\nNational weighted mean yield for {cropid} in {year}: {nationalMean.astype(int)} kg/ha\n')
                f.close()

                f = open(reportfile2, "a")
                #f.write(f'\nKokomaan keskisato viljalle {cropid} vuonna {year}: {dfall.iloc[:,-1].mean().astype(int)} kg/ha\n')
                f.write(f'\nKokomaan painotettu keskisato viljalle {cropid} vuonna {year}: {nationalMean.astype(int)} kg/ha\n')
                f.close()
                
                #maakuntakohtaiset = round(dfall.groupby('Maakunta').mean(),0)
                # Weighted:
                dfall3 = dfall[['Maakunta', 'tmp_weighted_yield', 'Area']].groupby('Maakunta').agg('sum')
                dfall3['weighted_yield'] = dfall3['tmp_weighted_yield'] / dfall3['Area'].astype(float)

                maakuntakohtaiset = round(dfall3[['Area', 'weighted_yield']], 0)

                outputfile = os.path.join(os.path.dirname(filename), cropid + '-' + 'maakunnittain.csv')
                #outputfilexls = os.path.join(os.path.dirname(filename), cropid + '-' + 'maakunnittain.xls')
                print(f'Saving maakuntakohtaiset into {outputfile}')
                maakuntakohtaiset.to_csv(outputfile, index = True)
                #maakuntakohtaiset.to_excel(outputfilexls, index = True)
                
                # boto3:               
                boto3file2 = cropid + '-' + pvm00 + '-maakunnittain.csv'
                print(f'Saving maakuntakohtaiset into Allas {boto3file2}')
                s3_resource.Object(my_bucketname, boto3file2).upload_file(outputfile, ExtraArgs={'ACL':'public-read'})
                
                # Save maakuntakohtaiset aikasarjat:
                
                results = []
                dfalltmp = dfall.drop('tmp_weighted_yield', axis = 1)

                for i in range(6, dfalltmp.shape[1]):
                    name = dfalltmp.columns[i]
                    
                    # Weighted yield by area:
                    dfalltmp['tmp_weighted_yield'] = dfalltmp.iloc[:,i] * dfalltmp['Area']

                    tmp = dfalltmp[['Maakunta', 'tmp_weighted_yield', 'Area']].groupby('Maakunta').agg('sum')
                    tmp[name] = tmp['tmp_weighted_yield'] / tmp['Area'].astype(float)
                    tmp2 = tmp.drop(['tmp_weighted_yield', 'Area'], axis = 1)
                    
                    results.append(tmp2)                        
                        
                dfMaakunta = pd.concat(results, axis = 1, ignore_index = False)
                
                outputfile = os.path.join(os.path.dirname(filename), cropid + '-aikasarja-maakunnittain.csv')
                dfMaakunta.astype(int).to_csv(outputfile, index = True)
    
                boto3file3 = cropid + '-aikasarja-maakunnittain.csv'
                print(f'Saving maakuntakohtaiset into Allas {boto3file3}')
                s3_resource.Object(my_bucketname, boto3file3).upload_file(outputfile, ExtraArgs={'ACL':'public-read'})
                
                
                # Save kuntakohtaiset aikasarjat:
                
                results = []
                dfalltmp = dfall.drop('tmp_weighted_yield', axis = 1)

                for i in range(6, dfalltmp.shape[1]):
                    name = dfalltmp.columns[i]
                    
                    # Weighted yield by area:
                    dfalltmp['tmp_weighted_yield'] = dfalltmp.iloc[:,i] * dfalltmp['Area']

                    tmp = dfalltmp[['Municipality', 'tmp_weighted_yield', 'Area']].groupby('Municipality').agg('sum')
                    tmp[name] = tmp['tmp_weighted_yield'] / tmp['Area'].astype(float)
                    tmp2 = tmp.drop(['tmp_weighted_yield', 'Area'], axis = 1)
                    
                    results.append(tmp2)                        
                        
                dfKunta = pd.concat(results, axis = 1, ignore_index = False)

                
                outputfile = os.path.join(os.path.dirname(filename), cropid + '-aikasarja-kunnittain.csv')
                dfKunta.astype(int).to_csv(outputfile, index = True)
    
                boto3file3 = cropid + '-aikasarja-kunnittain.csv'
                print(f'Saving kuntakohtaiset into Allas {boto3file3}')
                s3_resource.Object(my_bucketname, boto3file3).upload_file(outputfile, ExtraArgs={'ACL':'public-read'})
                
                # Save koko maan aikasarjat:
                
                results = []
                dfalltmp = dfall.drop('tmp_weighted_yield', axis = 1)
                
                for i in range(6, dfalltmp.shape[1]):
                    
                    name = dfalltmp.columns[i]
                    #print(name)
                    # weighted mean:
                    dfalltmp['tmp_weighted_yield'] = dfalltmp.iloc[:,i] * dfalltmp['Area']

                    tmp = dfalltmp[['tmp_weighted_yield', 'Area']].agg('sum')
                    tmp2 = tmp['tmp_weighted_yield'] / tmp['Area'].astype(float)
                    results.append([name, tmp2.astype(int)])

                dfMaa = pd.DataFrame(results, columns = ['Pvm', 'Keskisato (kg/ha)'])                
                outputfile = os.path.join(os.path.dirname(filename), cropid + '-aikasarja-koko-maa.csv')
                dfMaa.to_csv(outputfile, index = False)
                
                boto3file3 = cropid + '-aikasarja-koko-maa.csv'
                print(f'Saving koko maan ennusteet into Allas {boto3file3}')
                s3_resource.Object(my_bucketname, boto3file3).upload_file(outputfile, ExtraArgs={'ACL':'public-read'})
    

    
                
                                        
            except Exception as e:
                print('\n\nUnable to merge preds with parcels.')
                parser.print_help()
                raise e
        


            # If you want to see the list of Allas files:
            print(f'My files in Allas {my_bucketname}:')
            
            #my_bucket = s3_resource.Bucket(my_bucketname)
            
            #for my_bucket_object in my_bucket.objects.all():
            #    print(my_bucket_object.key)

            print(f'\nDone.')

    except Exception as e:
        print('\n\nUnable to read input or write out statistics. Check prerequisites and see exception output below.')
        parser.print_help()
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(__doc__))

    parser.add_argument('-i', '--inputpath',
                        help='Filepath of predictions.',
                        type=str)
    parser.add_argument('-b', '--bucketname',
                        help='Give a name of an existing bucket in S3.',
                        type=str)

    args = parser.parse_args()
    main(args)

