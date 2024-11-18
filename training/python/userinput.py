"""
Originally written by Samantha Wittke in 2020.
Modified by MY.

MY 2022-05-03 Bandlist args functional now.

Class for handling the userinput.

  
"""

import os
import argparse
import datetime


def none_or_int(value):
    if value == 'None':
        return None
    return int(value)


class UserInput(object):

    def __init__(self):
        self.getUserInput()

    def getUserInput(self):
      

        parser = argparse.ArgumentParser()
        
        #fill parser, startdate and enddate must be given, (enddate is todays date if not given, but does not work yet)
        parser.add_argument('-s', action='store', dest= 'startdate', type = str, help= 'give startdate in form YYYYMMDD')
        # warning: default (todays date) for enddate does not work yet ?!
        parser.add_argument('-e', action='store', dest= 'enddate', type = str, help= 'give enddate in form YYYYMMDD, default is todays date')
        #add argument for input shapefile
        parser.add_argument('-shp', action='store', dest= 'shapedir', help= 'give the path to dir with shapefiles of area to be investigated ')
        #add output filename for the textfile with paths
        parser.add_argument('-p', action='store', dest= 'projectname', help = 'give the full path to the projectfolder, where all the files should be saved')
        parser.add_argument('-t', action='store', dest= 'tmpdir', help = 'give the temporary direcfory path')
        #bandfile for secondpart puhti
        parser.add_argument('-f', action='store',dest='bandpath',help='file to be processed')
        #bands to be processed
        parser.add_argument('-b', action='store', dest='bandlist', nargs='+', type = int, help='bands to be processed')
        #path to data (S2 SAFE)
        parser.add_argument('-d', action='store',dest='datadir',help=' path to data')
        # name of ID field in shapefile
        parser.add_argument('-id', action='store',dest='idname',help='name of ID field in shapefile')
        #jobnumber from puthi array job
        parser.add_argument('-jn',action='store',dest='jobnumber')
        parser.add_argument('-r', type=none_or_int, dest='target_resolution_m')
        parser.add_argument('-c', action='store', type=str, dest='cloud_mask_path')

        #parse arguments
        args = parser.parse_args()
        self.saveArgs(args)


    def saveArgs(self, args):
      
        self.startdate = args.startdate
        self.enddate = args.enddate
        self.shapedir = args.shapedir
        self.projectname = args.projectname
        self.tmpdir = args.tmpdir
        self.bandpath = args.bandpath
        if args.bandlist is None:
            self.bandlist = [2,3,4,5,6,7,8,11,12,13]
        else:
            self.bandlist = args.bandlist
        self.datadir = args.datadir
        self.idname = args.idname
        self.jobnumber = args.jobnumber
        self.target_resolution_m = args.target_resolution_m
        self.cloud_mask_path = args.cloud_mask_path

