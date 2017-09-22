"""
main.py -- main code for Sciris users to change to create their web apps
    
Last update: 9/21/17 (gchadder3)
"""

#
# Imports
#

import scirismodel.model as model
import datastore as ds
import user
from flask_login import current_user
import mpld3
import os
import re
import uuid

#
# Classes
# NOTE: These probably should end up in other files (if I keep them).
#

# Wraps a Matplotlib figure displayable in the GUI.
class GraphFigure(object):
    def __init__(self, theFigure):
        self.theFigure = theFigure

# Wraps a collection of data.
class DataCollection(object):
    def __init__(self, dataObj):
        self.dataObj = dataObj

#
# Initialization functions 
#
        
def init_filepaths():
    # Set the Sciris root path to the parent of the current directory, the 
    # latter being the sciris/bin directory since that is where the code is 
    # executed from.
    ds.scirisRootPath = os.path.abspath(os.pardir)
    
    # Set the uploads path.
    ds.uploadsPath = '%s%s%s' % (ds.scirisRootPath, os.sep, 'uploads')
    
    # Set the file save root path.
    ds.fileSaveRootPath = '%s%s%s' % (ds.scirisRootPath, os.sep, 'savedfiles')
         
    # If the datafiles path doesn't exist yet...
    if not os.path.exists(ds.fileSaveRootPath):
        # Create datafiles directory.
        os.mkdir(ds.fileSaveRootPath)
        
        # Create an uploads subdirectory of this.
        os.mkdir(ds.uploadsPath)
        
        # Create the fake data for scatterplots.
        sd = model.ScatterplotData(model.makeUniformRandomData(50))
        fullFileName = '%s%sgraph1.csv' % (ds.fileSaveRootPath, os.sep)
        sd.saveAsCsv(fullFileName)
        
        sd = model.ScatterplotData(model.makeUniformRandomData(50))
        fullFileName = '%s%sgraph2.csv' % (ds.fileSaveRootPath, os.sep)
        sd.saveAsCsv(fullFileName)
        
        sd = model.ScatterplotData(model.makeUniformRandomData(50))
        fullFileName = '%s%sgraph3.csv' % (ds.fileSaveRootPath, os.sep)
        sd.saveAsCsv(fullFileName) 
        
def init_datastore():
    # Create the DataStore object, setting up Redis.
    ds.theDataStore = ds.DataStore(redisDbURL='redis://localhost:6379/1/')
    
    # Load the DataStore state from disk.
    ds.theDataStore.load()
    
def init_users():
    # Try to fetch the user dictionary from theDataStore.
    theUserDictUID = uuid.UUID('12345678123456781234567812345670')
    user.theUserDict = ds.theDataStore.retrieve(theUserDictUID)
    
    # If the entry is not found...
    if user.theUserDict is None:
        print '>> Created new user dictionary.'
        # Create a new UserDict (empty) object and store it in theDataStore.
        user.theUserDict = user.UserDict(theUserDictUID)
        ds.theDataStore.add(user.theUserDict, theUserDictUID, 
            theTypeLabel='userdict', theFileSuffix='.ud', 
            theInstanceLabel='Users Dictionary')
        
        # Add the two test users to this UserDict.
        user.theUserDict.add(user.testUser)
        user.theUserDict.add(user.testUser2)
    else:
        print '>> Loaded existing user dictionary.'

    # Show all of the handles in theDataStore.
    print '>> List of all DataStore handles...'
    ds.theDataStore.showHandles()
    
    # Show all of the users in theUserDict.
    print '>> List of all users...'
    user.theUserDict.showUsers()     

#
# Other functions
#

def get_saved_scatterplotdata_file_path(spdName):
    # Set the directory to the user's private directory.
    userFileSavePath = '%s%s%s' % (ds.fileSaveRootPath, os.sep, 
        current_user.username)
    
    # Create a full file name for the file.
    fullFileName = '%s%s%s.csv' % (userFileSavePath, os.sep, spdName)
    
    # If the file is there, return the path name; otherwise, return None.
    if os.path.exists(fullFileName):
        return fullFileName
    else:
        return None
    
#
# RPC functions
#

def list_saved_scatterplotdata_resources():
    # Set the directory to the user's private directory.
    userFileSavePath = '%s%s%s' % (ds.fileSaveRootPath, os.sep, 
        current_user.username)
    
    # If the directory doesn't exist, return an empty list.
    if not os.path.exists(userFileSavePath):
        return []
    
    # Get the total list of entries in the user's directory.
    allEntries = os.listdir(userFileSavePath)
    
    # Extract just the entries that are .csv files.
    fTypeEntries = [entry for entry in allEntries if re.match('.+\.csv$', entry)]
    
    # Truncate the .csv suffix from each entry.
    truncEntries = [re.sub('\.csv$', '', entry) for entry in fTypeEntries]
    
    # Return the truncated entries.
    return truncEntries

def get_saved_scatterplotdata_graph(spdName):
    # Look for a match of the resource, and if we don't find it, return
    # an error.
    fullFileName = get_saved_scatterplotdata_file_path(spdName)
    if fullFileName is None:
        return {'error': 'Cannot find resource \'%s\'' % spdName}
    
    # Create a ScatterplotData object.
    spd = model.ScatterplotData()

    # Load the data for this from the csv file.
    spd.loadFromCsv(fullFileName)
    
    # Generate a matplotib graph for display.
    graphData = spd.plot()
    
    # Return the dictionary representation of the matplotlib figure.
    return mpld3.fig_to_dict(graphData) 

def download_saved_scatterplotdata(spdName):
    return get_saved_scatterplotdata_file_path(spdName)

def upload_scatterplotdata_from_csv(fullFileName, spdName):
    # Set the directory to the user's private directory.
    userFileSavePath = '%s%s%s' % (ds.fileSaveRootPath, os.sep, 
        current_user.username)
    
    # If the directory doesn't exist yet, make it.
    if not os.path.exists(userFileSavePath):
        os.mkdir(userFileSavePath)
    
    # Pull out the directory and file names from the full file name.
    dirName, fileName = os.path.split(fullFileName)
    
    # Create a new destination for the file in the datafiles directory.
    newFullFileName = '%s%s%s' % (userFileSavePath, os.sep, fileName)
    
    # Move the file into the datafiles directory.
    os.rename(fullFileName, newFullFileName)
    
    # Return the new file name.
    return newFullFileName
