#############################################################################################################################
### Imports
#############################################################################################################################

try:    import cPickle as pickle # For Python 3 compatibility
except: import pickle
from gzip import GzipFile
from cStringIO import StringIO
from contextlib import closing
from sciris.utils import makefilepath, odict, dataframe
from xlrd import open_workbook



#############################################################################################################################
### Basic I/O functions
#############################################################################################################################

def dumpstr(obj):
    ''' Write data to a fake file object,then read from it -- used on the FE '''
    result = None
    with closing(StringIO()) as output:
        with GzipFile(fileobj = output, mode = 'wb') as fileobj: 
            fileobj.write(pickle.dumps(obj, protocol=-1))
        output.seek(0)
        result = output.read()
    return result


def loadstr(source):
    ''' Load data from a fake file object -- also used on the FE '''
    with closing(StringIO(source)) as output:
        with GzipFile(fileobj = output, mode = 'rb') as fileobj: 
            obj = loadpickle(fileobj)
    return obj


def loadpickle(fileobj, verbose=False):
    ''' Loads a pickled object -- need to define legacy classes here since they're needed for unpickling '''
    
    # Load the file string
    filestr = fileobj.read()
    
    try: # Try just loading it
        obj = pickle.loads(filestr) # Actually load it
    except Exception as E: # If that fails, create legacy classes and try again
        raise E
    
    return obj


def loadspreadsheet(filename=None, folder=None, sheetname=None, sheetnum=None, asdataframe=True):
    '''
    Load a spreadsheet
    '''

    fullpath = makefilepath(filename=filename, folder=folder)
    workbook = open_workbook(fullpath)
    if sheetname is not None: 
        sheet = workbook.sheet_by_name(sheetname)
    else:
        if sheetnum is None: sheetnum = 0
        sheet = workbook.sheet_by_index(sheetnum)
    
    # Load the raw data
    rawdata = []
    for rownum in range(sheet.nrows-1):
        rawdata.append(odict())
        for colnum in range(sheet.ncols):
            attr = sheet.cell_value(0,colnum)
            val = sheet.cell_value(rownum+1,colnum)
            try:    val = float(val) # Convert it to a number if possible
            except: 
                try:    val = str(val)  # But give up easily and convert to a string (not Unicode)
                except: pass # Still no dice? Fine, we tried
            rawdata[rownum][attr] = val
    
    # Convert to dataframe
    if asdataframe:
        cols = rawdata[0].keys()
        reformatted = []
        for oldrow in rawdata:
            newrow = list(oldrow[:])
            reformatted.append(newrow)
        dfdata = dataframe(cols=cols, data=reformatted)
        return dfdata
    
    # Or leave in the original format
    else:
        return rawdata