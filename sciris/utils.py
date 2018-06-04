##############################################################################
### IMPORTS FROM OTHER LIBRARIES
##############################################################################

import numpy as np


# Handle types and Python 2/3 compatibility
from six import PY2 as _PY2
from numbers import Number as _numtype
if _PY2: _stringtype = basestring 
else:    _stringtype = str

def uuid(which=None):
    ''' Shortcut for creating a UUID; default is to create a UUID4. '''
    import uuid
    if which is None: which = 4
    if   which==1: output = uuid.uuid1()
    elif which==3: output = uuid.uuid3()
    elif which==4: output = uuid.uuid4()
    elif which==5: output = uuid.uuid5()
    else: raise Exception('UUID type %i not recognized; must be 1,  3, , or 5)' % which)
    
    return output

def dcp(obj=None):
    ''' Shortcut to perform a deep copy operation '''
    import copy
    return copy.deepcopy(obj)


##############################################################################
### PRINTING/NOTIFICATION FUNCTIONS
##############################################################################

def printv(string, thisverbose=1, verbose=2, newline=True, indent=True):
    '''
    Optionally print a message and automatically indent. The idea is that
    a global or shared "verbose" variable is defined, which is passed to
    subfunctions, determining how much detail to print out.

    The general idea is that verbose is an integer from 0-4 as follows:
        0 = no printout whatsoever
        1 = only essential warnings, e.g. suppressed exceptions
        2 = standard printout
        3 = extra debugging detail (e.g., printout on each iteration)
        4 = everything possible (e.g., printout on each timestep)
    
    Thus a very important statement might be e.g.
        printv('WARNING, everything is wrong', 1, verbose)

    whereas a much less important message might be
        printv('This is timestep %i' % i, 4, verbose)

    Version: 2016jan30
    '''
    if thisverbose>4 or verbose>4: print('Warning, verbosity should be from 0-4 (this message: %i; current: %i)' % (thisverbose, verbose))
    if verbose>=thisverbose: # Only print if sufficiently verbose
        indents = '  '*thisverbose*bool(indent) # Create automatic indenting
        if newline: print(indents+flexstr(string)) # Actually print
        else: print(indents+flexstr(string)), # Actually print
    return None


def blank(n=3):
    ''' Tiny function to print n blank lines, 3 by default '''
    print('\n'*n)


def createcollist(oldkeys, title, strlen = 18, ncol = 3):
    ''' Creates a string for a nice columnated list (e.g. to use in __repr__ method) '''
    nrow = int(np.ceil(float(len(oldkeys))/ncol))
    newkeys = []
    for x in range(nrow):
        newkeys += oldkeys[x::nrow]
    
    attstring = title + ':'
    c = 0    
    for x in newkeys:
        if c%ncol == 0: attstring += '\n  '
        if len(x) > strlen: x = x[:strlen-3] + '...'
        attstring += '%-*s  ' % (strlen,x)
        c += 1
    attstring += '\n'
    return attstring


def objectid(obj):
    ''' Return the object ID as per the default Python __repr__ method '''
    output = '<%s.%s at %s>\n' % (obj.__class__.__module__, obj.__class__.__name__, hex(id(obj)))
    return output


def objatt(obj, strlen=18, ncol=3):
    ''' Return a sorted string of object attributes for the Python __repr__ method '''
    oldkeys = sorted(obj.__dict__.keys())
    output = createcollist(oldkeys, 'Attributes', strlen = 18, ncol = 3)
    return output


def objmeth(obj, strlen=18, ncol=3):
    ''' Return a sorted string of object methods for the Python __repr__ method '''
    oldkeys = sorted([method + '()' for method in dir(obj) if callable(getattr(obj, method)) and not method.startswith('__')])
    output = createcollist(oldkeys, 'Methods', strlen=strlen, ncol=ncol)
    return output


def objrepr(obj, showid=True, showmeth=True, showatt=True):
    ''' Return useful printout for the Python __repr__ method '''
    divider = '============================================================\n'
    output = ''
    if showid:
        output += objectid(obj)
        output += divider
    if showmeth:
        output += objmeth(obj)
        output += divider
    if showatt:
        output += objatt(obj)
        output += divider
    return output


def desc(obj, maxlen=None):
    ''' Prints out the default representation of an object -- all attributes, plust methods and ID '''
    if maxlen is None: maxlen = 80
    keys = sorted(obj.__dict__.keys()) # Get the attribute keys
    maxkeylen = max([len(key) for key in keys]) # Find the maximum length of the attribute keys
    if maxkeylen<maxlen: maxlen = maxlen - maxkeylen # Shorten the amount of data shown if the keys are long
    formatstr = '%'+ '%i'%maxkeylen + 's' # Assemble the format string for the keys, e.g. '%21s'
    output  = objrepr(obj, showatt=False) # Get the methods
    for key in keys: # Loop over each attribute
        thisattr = flexstr(getattr(obj, key)) # Get the string representation of the attribute
        if len(thisattr)>maxlen: thisattr = thisattr[:maxlen] + ' [...]' # Shorten it
        prefix = formatstr%key + ': ' # The format key
        output += indent(prefix, thisattr)
    output += '============================================================\n'

    return output


def printdr(obj, maxlen=None):
    ''' Shortcut for printing the default repr for an object '''
    print(desc(obj, maxlen=maxlen))
    return None

    
def indent(prefix=None, text=None, suffix='\n', n=0, pretty=False, simple=True, width=70, **kwargs):
    '''
    Small wrapper to make textwrap more user friendly.
    
    Arguments:
        prefix = text to begin with (optional)
        text = text to wrap
        suffix = what to put on the end (by default, a newline)
        n = if prefix is not specified, the size of the indent
        prettify = whether to use pprint to format the text
        kwargs = anything to pass to textwrap.fill() (e.g., linewidth)
    
    Examples:
        prefix = 'and then they said:'
        text = 'blah '*100
        print(indent(prefix, text))
        
        print('my fave is: ' + indent(text=rand(100), n=14))
    
    Version: 2017feb20
    '''
    # Imports
    from textwrap import fill
    from pprint import pformat
    
    # Handle no prefix
    if prefix is None: prefix = ' '*n
    
    # Get text in the right format -- i.e. a string
    if pretty: text = pformat(text)
    else:      text = flexstr(text)

    # If there is no newline in the text, process the output normally.
    if text.find('\n') == -1:
        output = fill(text, initial_indent=prefix, subsequent_indent=' '*len(prefix), width=width, **kwargs)+suffix
    # Otherwise, handle each line separately and splice together the output.
    else:
        textlines = text.split('\n')
        output = ''
        for i, textline in enumerate(textlines):
            if i == 0:
                theprefix = prefix
            else:
                theprefix = ' '*len(prefix)
            output += fill(textline, initial_indent=theprefix, subsequent_indent=' '*len(prefix), width=width, **kwargs)+suffix
    
    if n: output = output[n:] # Need to remove the fake prefix
    return output
    


def sigfig(X, sigfigs=5, SI=False, sep=False):
    '''
    Return a string representation of variable x with sigfigs number of significant figures -- 
    copied from asd.py.
    
    If SI=True,  then will return e.g. 32433 as 32.433K
    If sep=True, then will return e.g. 32433 as 32,433
    '''
    output = []
    
    try: 
        n=len(X)
        islist = True
    except:
        X = [X]
        n = 1
        islist = False
    for i in range(n):
        x = X[i]
        
        suffix = ''
        formats = [(1e18,'e18'), (1e15,'e15'), (1e12,'t'), (1e9,'b'), (1e6,'m'), (1e3,'k')]
        if SI:
            for val,suff in formats:
                if abs(x)>=val:
                    x = x/val
                    suffix = suff
                    break # Find at most one match
        
        try:
            if x==0:
                output.append('0')
            elif sigfigs is None:
                output.append(flexstr(x)+suffix)
            else:
                magnitude = np.floor(np.log10(abs(x)))
                factor = 10**(sigfigs-magnitude-1)
                x = round(x*factor)/float(factor)
                digits = int(abs(magnitude) + max(0, sigfigs - max(0,magnitude) - 1) + 1 + (x<0) + (abs(x)<1)) # one because, one for decimal, one for minus
                decimals = int(max(0,-magnitude+sigfigs-1))
                strformat = '%' + '%i.%i' % (digits, decimals)  + 'f'
                string = strformat % x
                if sep: # To insert separators in the right place, have to convert back to a number
                    if decimals>0:  roundnumber = float(string)
                    else:           roundnumber = int(string)
                    string = format(roundnumber, ',') # Allow comma separator
                string += suffix
                output.append(string)
        except:
            output.append(flexstr(x))
    if islist:
        return tuple(output)
    else:
        return output[0]



def printarr(arr, arrformat='%0.2f  '):
    ''' 
    Print a numpy array nicely.
    
    Example:
        from utils import printarr
        from numpy import random
        printarr(rand(3,7,4))
    
    Version: 2014dec01
    '''
    if np.ndim(arr)==1:
        string = ''
        for i in range(len(arr)):
            string += arrformat % arr[i]
        print(string)
    elif np.ndim(arr)==2:
        for i in range(len(arr)):
            printarr(arr[i], arrformat)
    elif np.ndim(arr)==3:
        for i in range(len(arr)):
            print('='*len(arr[i][0])*len(arrformat % 1))
            for j in range(len(arr[i])):
                printarr(arr[i][j], arrformat)
    else:
        print(arr) # Give up
    return None



def printdata(data, name='Variable', depth=1, maxlen=40, indent='', level=0, showcontents=False):
    '''
    Nicely print a complicated data structure, a la Matlab.
    Arguments:
      data: the data to display
      name: the name of the variable (automatically read except for first one)
      depth: how many levels of recursion to follow
      maxlen: number of characters of data to display (if 0, don't show data)
      indent: where to start the indent (used internally)
    
    Version: 1.0 (2015aug21)    
    '''
    datatype = type(data)
    def printentry(data):
        if   datatype==dict:              string = ('dict with %i keys' % len(data.keys()))
        elif datatype==list:              string = ('list of length %i' % len(data))
        elif datatype==tuple:             string = ('tuple of length %i' % len(data))
        elif datatype==np.ndarray:        string = ('array of shape %s' % flexstr(np.shape(data)))
        elif datatype.__name__=='module': string = ('module with %i components' % len(dir(data)))
        elif datatype.__name__=='class':  string = ('class with %i components' % len(dir(data)))
        else: string = datatype.__name__
        if showcontents and maxlen>0:
            datastring = ' | '+flexstr(data)
            if len(datastring)>maxlen: datastring = datastring[:maxlen] + ' <etc> ' + datastring[-maxlen:]
        else: datastring=''
        return string+datastring
    
    string = printentry(data).replace('\n',' \ ') # Remove newlines
    print(level*'..' + indent + name + ' | ' + string)

    if depth>0:
        level += 1
        if type(data)==dict:
            keys = data.keys()
            maxkeylen = max([len(key) for key in keys])
            for key in keys:
                thisindent = ' '*(maxkeylen-len(key))
                printdata(data[key], name=key, depth=depth-1, indent=indent+thisindent, level=level)
        elif type(data) in [list, tuple]:
            for i in range(len(data)):
                printdata(data[i], name='[%i]'%i, depth=depth-1, indent=indent, level=level)
        elif type(data).__name__ in ['module', 'class']:
            keys = dir(data)
            maxkeylen = max([len(key) for key in keys])
            for key in keys:
                if key[0]!='_': # Skip these
                    thisindent = ' '*(maxkeylen-len(key))
                    printdata(getattr(data,key), name=key, depth=depth-1, indent=indent+thisindent, level=level)
        print('\n')
    return None


def printvars(localvars=None, varlist=None, label=None, divider=True, spaces=1, color=None):
    '''
    Print out a list of variables. Note that the first argument must be locals().
    
    Arguments:
        localvars = function must be called with locals() as first argument
        varlist = the list of variables to print out
        label = optional label to print out, so you know where the variables came from
        divider = whether or not to offset the printout with a spacer (i.e. ------)
        spaces = how many spaces to use between variables
        color = optionally label the variable names in color so they're easier to see
    
    Simple usage example:
        a = range(5); b = 'example'; printvars(locals(), ['a','b'], color='blue')
    
    Another useful usage case is to print out the kwargs for a function:
        printvars(locals(), kwargs.keys())
        
    Version: 2017oct28
    '''
    
    varlist = promotetolist(varlist) # Make sure it's actually a list
    dividerstr = '-'*40
    
    if label:  print('Variables for %s:' % label)
    if divider: print(dividerstr)
    for varnum,varname in enumerate(varlist):
        controlstr = '%i. "%s": ' % (varnum, varname) # Basis for the control string -- variable number and name
        if color: controlstr = colorize(color, output=True) + controlstr + colorize('reset', output=True) # Optionally add color
        if spaces>1: controlstr += '\n' # Add a newline if the variables are going to be on different lines
        try:    controlstr += '%s' % localvars[varname] # The variable to be printed
        except: controlstr += 'WARNING, could not be printed' # In case something goes wrong
        controlstr += '\n' * spaces # The number of spaces to add between variables
        print(controlstr), # Print it out
    if divider: print(dividerstr) # If necessary, print the divider again
    return None


def today(timezone='utc', die=False):
    ''' Get the current time, in UTC time '''
    import datetime # today = datetime.today
    try:
        import dateutil
        if timezone=='utc':                           tzinfo = dateutil.tz.tzutc()
        elif timezone is None or timezone=='current': tzinfo = None
        else:                                         raise Exception('Timezone "%s" not understood' % timezone)
    except:
        errormsg = 'Timezone information not available'
        if die: raise Exception(errormsg)
        tzinfo = None
    now = datetime.datetime.now(tzinfo)
    return now


def getdate(obj, which='modified', fmt='str'):
        ''' Return either the date created or modified ("which") as either a str or int ("fmt") '''
        from time import mktime
        
        dateformat = '%Y-%b-%d %H:%M:%S'
        
        try:
            if isstring(obj): return obj # Return directly if it's a string
            obj.timetuple() # Try something that will only work if it's a date object
            dateobj = obj # Test passed: it's a date object
        except: # It's not a date object
            if which=='created': dateobj = obj.created
            elif which=='modified': dateobj = obj.modified
            elif which=='spreadsheet': dateobj = obj.spreadsheetdate
            else: raise Exception('Getting date for "which=%s" not understood; must be "created", "modified", or "spreadsheet"' % which)
        
        if fmt=='str':
            try:
                return dateobj.strftime(dateformat).encode('ascii', 'ignore') # Return string representation of time
            except UnicodeDecodeError:
                dateformat = '%Y-%m-%d %H:%M:%S'
                return dateobj.strftime(dateformat)
        elif fmt=='int': return mktime(dateobj.timetuple()) # So ugly!! But it works -- return integer representation of time
        else: raise Exception('"fmt=%s" not understood; must be "str" or "int"' % fmt)




def slacknotification(to=None, message=None, fromuser=None, token=None, verbose=2, die=False):
    ''' 
    Send a Slack notification when something is finished.
    
    Arguments:
        to:
            The Slack channel or user to post to. Note that channels begin with #, while users begin with @.
        message:
            The message to be posted.
        fromuser:
            The pseudo-user the message will appear from.
        token:
            This must be a plain text file containing a single line which is the Slack API URL token.
            Tokens are effectively passwords and must be kept secure. If you need one, contact me.
        verbose:
            How much detail to display.
        die:
            If false, prints warnings. If true, raises exceptions.
    
    Example usage:
        slacknotification('#athena', 'Long process is finished')
        slacknotification(token='/.slackurl', channel='@username', message='Hi, how are you going?')
    
    What's the point? Add this to the end of a very long-running script to notify
    your loved ones that the script has finished.
        
    Version: 2017feb09
    '''
    
    # Imports
    from requests import post # Simple way of posting data to a URL
    from json import dumps # For sanitizing the message
    from getpass import getuser # In case username is left blank
    
    # Validate input arguments
    printv('Sending Slack message...', 2, verbose)
    if token is None:    token = '/.slackurl'
    if to is None:       to = '#general'
    if fromuser is None: fromuser = getuser()+'-bot'
    if message is None:  message = 'This is an automated notification: your notifier is notifying you.'
    printv('Channel: %s | User: %s | Message: %s' % (to, fromuser, message), 3, verbose) # Print details of what's being sent
    
    # Try opening token file    
    try:
        with open(token) as f: slackurl = f.read()
    except:
        print('Could not open Slack URL/token file "%s"' % token)
        if die: raise
        else: return None
    
    # Package and post payload
    payload = '{"text": %s, "channel": %s, "username": %s}' % (dumps(message), dumps(to), dumps(fromuser))
    printv('Full payload: %s' % payload, 4, verbose)
    response = post(url=slackurl, data=payload)
    printv(response, 3, verbose) # Optionally print response
    printv('Message sent.', 1, verbose) # We're done
    return None


def printtologfile(message=None, filename=None):
    '''
    Append a message string to a file specified by a filename name/path.  This 
    is especially useful for capturing information from spawned processes not 
    so handily captured through print statements.
    Warning: If you pass a file in, existing or not, it will try to append
    text to it!
    '''
    
    # Set defaults
    if message is None:  
        return None # Return immediately if nothing to append
    if filename is None: 
        filename = '/tmp/logfile' # Some generic filename that should work on *nix systems
    
    # Try writing to file
    try:
        with open(filename, 'a') as f:
            f.write('\n'+message+'\n') # Add a newline to the message.
    except: # Fail gracefully
        print('WARNING, could not write to logfile %s' % filename)
    
    return None
    

def colorize(color=None, string=None, output=False):
    '''
    Colorize output text. Arguments:
        color = the color you want (use 'bg' with background colors, e.g. 'bgblue')
        string = the text to be colored
        output = whether to return the modified version of the string
    
    Examples:
        colorize('green', 'hi') # Simple example
        colorize(['yellow', 'bgblack']); print('Hello world'); print('Goodbye world'); colorize() # Colorize all output in between
        bluearray = colorize(color='blue', string=str(range(5)), output=True); print("c'est bleu: " + bluearray)
        colorize('magenta') # Now type in magenta for a while
        colorize() # Stop typing in magenta
    
    To get available colors, type colorize('help').
    
    Note: although implemented as a class (to allow the "with" syntax),
    this actually functions more like a function.
    
    Version: 2017oct27
    '''
    
    # Define ANSI colors
    ansicolors = dict([
                  ('black', '30'),
                  ('red', '31'),
                  ('green', '32'),
                  ('yellow', '33'),
                  ('blue', '34'),
                  ('magenta', '35'),
                  ('cyan', '36'),
                  ('gray', '37'),
                  ('bgblack', '40'),
                  ('bgred', '41'),
                  ('bggreen', '42'),
                  ('bgyellow', '43'),
                  ('bgblue', '44'),
                  ('bgmagenta', '45'),
                  ('bgcyan', '46'),
                  ('bggray', '47'),
                  ('reset', '0'),
                  ])
    for key,val in ansicolors.items(): ansicolors[key] = '\033['+val+'m'
    
    # Determine what color to use
    if color is None: color = 'reset' # By default, reset
    colorlist = promotetolist(color) # Make sure it's a list
    for color in colorlist:
        if color not in ansicolors.keys(): 
            if color!='help': print('Color "%s" is not available.' % color)
            print('Available colors are:  \n%s' % '\n  '.join(ansicolors.keys()))
            return None # Don't proceed if no color supplied
    ansicolor = ''
    for color in colorlist:
        ansicolor += ansicolors[color]
    
    # Modify string, if supplied
    if string is None: ansistring = ansicolor # Just return the color
    else:              ansistring = ansicolor + str(string) + ansicolors['reset'] # Add to start and end of the string

    if output: 
        return ansistring # Return the modified string
    else:
        print(ansistring) # Content, so print with newline
        return None
    


        
    
##############################################################################
### TYPE FUNCTIONS
##############################################################################

def flexstr(arg):
    ''' Try converting to a regular string, but proceed if it fails '''
    try:    output = str(arg)
    except: output = arg
    return  output


def isiterable(obj):
    '''
    Simply determine whether or not the input is iterable, since it's too hard to remember this otherwise.
    From http://stackoverflow.com/questions/1952464/in-python-how-do-i-determine-if-an-object-is-iterable
    '''
    try:
        iter(obj)
        return True
    except:
        return False
    

def checktype(obj=None, objtype=None, subtype=None, die=False):
    ''' 
    A convenience function for checking instances. If objtype is a type,
    then this function works exactly like isinstance(). But, it can also
    be a string, e.g. 'array'.
    
    If subtype is not None, then checktype will iterate over obj and check
    recursively that each element matches the subtype.
    
    Arguments:
        obj     = the object to check the type of
        objtype = the type to confirm the object belongs to
        subtype = optionally check the subtype if the object is iterable
        die     = whether or not to raise an exception if the object is the wrong type.
    
    Examples:
        checktype(rand(10), 'array', 'number') # Returns true
        checktype(['a','b','c'], 'arraylike') # Returns false
        checktype([{'a':3}], list, dict) # Returns True
    '''
    # Handle "objtype" input
    if   objtype in ['str','string']:  objinstance = _stringtype
    elif objtype in ['num', 'number']: objinstance = _numtype
    elif objtype in ['arr', 'array']:  objinstance = type(np.array([]))
    elif objtype=='arraylike':         objinstance = (list, tuple, type(np.array([]))) # Anything suitable as a numerical array
    elif type(objtype)==type:          objinstance = objtype  # Don't need to do anything
    elif objtype is None:              return None # If not supplied, exit
    else:
        errormsg = 'Could not understand what type you want to check: should be either a string or a type, not "%s"' % objtype
        raise Exception(errormsg)
    
    # Do first-round checking
    result = isinstance(obj, objinstance)
    
    # Do second round checking
    if result and objtype=='arraylike': # Special case for handling arrays which may be multi-dimensional
        obj = promotetoarray(obj).flatten() # Flatten all elements
        if subtype is None: subtype = 'number' # This is the default
    if isiterable(obj) and subtype is not None:
        for item in obj:
            result = result and checktype(item, subtype)

    # Decide what to do with the information thus gleaned
    if die: # Either raise an exception or do nothing if die is True
        if not result: # It's not an instance
            errormsg = 'Incorrect type: object is %s, but %s is required' % (type(obj), objtype)
            raise Exception(errormsg)
        else:
            return None # It's fine, do nothing
    else: # Return the result of the comparison
        return result
   
         
def isnumber(obj):
    ''' Simply determine whether or not the input is a number, since it's too hard to remember this otherwise '''
    return checktype(obj, 'number')
    
    
def isstring(obj):
    ''' Simply determine whether or not the input is a string, since it's too hard to remember this otherwise '''
    return checktype(obj, 'string')


def promotetoarray(x):
    ''' Small function to ensure consistent format for things that should be arrays '''
    if isnumber(x):
        return np.array([x]) # e.g. 3
    elif isinstance(x, (list, tuple)):
        return np.array(x) # e.g. [3]
    elif isinstance(x, np.ndarray): 
        if np.shape(x):
            return x # e.g. array([3])
        else: 
            return np.array([x]) # e.g. array(3)
    else: # e.g. 'foo'
        raise Exception("Expecting a number/list/tuple/ndarray; got: %s" % flexstr(x))


def promotetolist(obj=None, objtype=None):
    ''' Make sure object is iterable -- used so functions can handle inputs like 'FSW' or ['FSW', 'MSM'] '''
    if type(obj)!=list:
        obj = [obj] # Listify it
    if objtype is not None:  # Check that the types match -- now that we know it's a list, we can iterate over it
        for item in obj:
            checktype(obj=item, objtype=objtype, die=True)
    if obj is None:
        raise Exception('This is mathematically impossible')
    return obj






##############################################################################
### MATHEMATICAL FUNCTIONS
##############################################################################


def quantile(data, quantiles=[0.5, 0.25, 0.75]):
    '''
    Custom function for calculating quantiles most efficiently for a given dataset.
        data = a list of arrays, or an array where he first dimension is to be sorted
        quantiles = a list of floats >=0 and <=1
    
    Version: 2014nov23
    '''
    nsamples = len(data) # Number of samples in the dataset
    indices = (np.array(quantiles)*(nsamples-1)).round().astype(int) # Calculate the indices to pull out
    output = np.array(data)
    output.sort(axis=0) # Do the actual sorting along the 
    output = output[indices] # Trim down to the desired quantiles
    
    return output



def sanitize(data=None, returninds=False, replacenans=None, die=True):
        '''
        Sanitize input to remove NaNs. Warning, does not work on multidimensional data!!
        
        Examples:
            sanitized,inds = sanitize(array([3,4,nan,8,2,nan,nan,nan,8]), returninds=True)
            sanitized = sanitize(array([3,4,nan,8,2,nan,nan,nan,8]), replacenans=True)
            sanitized = sanitize(array([3,4,nan,8,2,nan,nan,nan,8]), replacenans=0)
        '''
        try:
            data = np.array(data,dtype=float) # Make sure it's an array of float type
            inds = np.nonzero(~np.isnan(data))[0] # WARNING, nonzero returns tuple :(
            sanitized = data[inds] # Trim data
            if replacenans is not None:
                newx = range(len(data)) # Create a new x array the size of the original array
                if replacenans==True: replacenans = 'nearest'
                if replacenans in ['nearest','linear']:
                    sanitized = smoothinterp(newx, inds, sanitized, method=replacenans, smoothness=0) # Replace nans with interpolated values
                else:
                    naninds = inds = np.nonzero(np.isnan(data))[0]
                    sanitized = dcp(data)
                    sanitized[naninds] = replacenans
            if len(sanitized)==0:
                sanitized = 0.0
                print('                WARNING, no data entered for this parameter, assuming 0')
        except Exception as E:
            if die: 
                raise Exception('Sanitization failed on array: "%s":\n %s' % (repr(E), data))
            else:
                sanitized = data # Give up and just return an empty array
                inds = []
        if returninds: return sanitized, inds
        else:          return sanitized


def getvaliddata(data=None, filterdata=None, defaultind=0):
    '''
    Return the years that are valid based on the validity of the input data.
    
    Example:
        getvaliddata(array([3,5,8,13]), array([2000, nan, nan, 2004])) # Returns array([3,13])
    '''
    data = np.array(data)
    if filterdata is None: filterdata = data # So it can work on a single input -- more or less replicates sanitize() then
    filterdata = np.array(filterdata)
    if filterdata.dtype=='bool': validindices = filterdata # It's already boolean, so leave it as is
    else:                        validindices = ~np.isnan(filterdata) # Else, assume it's nans that need to be removed
    if validindices.any(): # There's at least one data point entered
        if len(data)==len(validindices): # They're the same length: use for logical indexing
            validdata = np.array(np.array(data)[validindices]) # Store each year
        elif len(validindices)==1: # They're different lengths and it has length 1: it's an assumption
            validdata = np.array([np.array(data)[defaultind]]) # Use the default index; usually either 0 (start) or -1 (end)
        else:
            raise Exception('Array sizes are mismatched: %i vs. %i' % (len(data), len(validindices)))    
    else: 
        validdata = np.array([]) # No valid data, return an empty array
    return validdata



def getvalidinds(data=None, filterdata=None):
    '''
    Return the years that are valid based on the validity of the input data from an arbitrary number
    of 1-D vector inputs. Warning, closely related to getvaliddata()!
    
    Example:
        getvalidinds([3,5,8,13], [2000, nan, nan, 2004]) # Returns array([0,3])
    '''
    data = promotetoarray(data)
    if filterdata is None: filterdata = data # So it can work on a single input -- more or less replicates sanitize() then
    filterdata = promotetoarray(filterdata)
    if filterdata.dtype=='bool': filterindices = filterdata # It's already boolean, so leave it as is
    else:                        filterindices = findinds(~np.isnan(filterdata)) # Else, assume it's nans that need to be removed
    dataindices = findinds(~np.isnan(data)) # Also check validity of data
    validindices = np.intersect1d(dataindices, filterindices)
    return validindices # Only return indices -- WARNING, not consistent with sanitize()



def findinds(val1, val2=None, eps=1e-6):
    '''
    Little function to find matches even if two things aren't eactly equal (eg. 
    due to floats vs. ints). If one argument, find nonzero values. With two arguments,
    check for equality using eps. Returns a tuple of arrays if val1 is multidimensional,
    else returns an array.
    
    Examples:
        findinds(rand(10)<0.5) # e.g. array([2, 4, 5, 9])
        findinds([2,3,6,3], 6) # e.g. array([2])
    
    Version: 2016jun06 
    '''
    if val2==None: # Check for equality
        output = np.nonzero(val1) # If not, just check the truth condition
    else:
        if isstring(val2):
            output = np.nonzero(np.array(val1)==val2)
        else:
            output = np.nonzero(abs(np.array(val1)-val2)<eps) # If absolute difference between the two values is less than a certain amount
    if np.ndim(val1)==1: # Uni-dimensional
        output = output[0] # Return an array rather than a tuple of arrays if one-dimensional
    return output



def findnearest(series=None, value=None):
    '''
    Return the index of the nearest match in series to value -- like findinds, but
    always returns an object with the same type as value (i.e. findnearest with
    a number returns a number, findnearest with an array returns an array).
    
    Examples:
        findnearest(rand(10), 0.5) # returns whichever index is closest to 0.5
        findnearest([2,3,6,3], 6) # returns 2
        findnearest([2,3,6,3], 6) # returns 2
        findnearest([0,2,4,6,8,10], [3, 4, 5]) # returns array([1, 2, 2])
    
    Version: 2017jan07
    '''
    series = promotetoarray(series)
    if isnumber(value):
        output = np.argmin(abs(series-value))
    else:
        output = []
        for val in value: output.append(findnearest(series, val))
        output = promotetoarray(output)
    return output
    
    
def dataindex(dataarray, index):        
    ''' Take an array of data and return either the first or last (or some other) non-NaN entry. '''
    
    nrows = np.shape(dataarray)[0] # See how many rows need to be filled (either npops, nprogs, or 1).
    output = np.zeros(nrows)       # Create structure
    for r in range(nrows): 
        output[r] = sanitize(dataarray[r])[index] # Return the specified index -- usually either the first [0] or last [-1]
    
    return output


def smoothinterp(newx=None, origx=None, origy=None, smoothness=None, growth=None, ensurefinite=False, keepends=True, method='linear'):
    '''
    Smoothly interpolate over values and keep end points. Same format as numpy.interp.
    
    Example:
        from utils import smoothinterp
        origy = array([0,0.1,0.3,0.8,0.7,0.9,0.95,1])
        origx = linspace(0,1,len(origy))
        newx = linspace(0,1,5*len(origy))
        newy = smoothinterp(newx, origx, origy, smoothness=5)
        plot(newx,newy)
        hold(True)
        scatter(origx,origy)
    
    Version: 2018jan24
    '''
    # Ensure arrays and remove NaNs
    if isnumber(newx):  newx = [newx] # Make sure it has dimension
    if isnumber(origx): origx = [origx] # Make sure it has dimension
    if isnumber(origy): origy = [origy] # Make sure it has dimension
    newx  = np.array(newx)
    origx = np.array(origx)
    origy = np.array(origy)
    
    # If only a single element, just return it, without checking everything else
    if len(origy)==1: 
        newy = np.zeros(newx.shape)+origy[0]
        return newy
    
    if not(newx.shape): raise Exception('To interpolate, must have at least one new x value to interpolate to')
    if not(origx.shape): raise Exception('To interpolate, must have at least one original x value to interpolate to')
    if not(origy.shape): raise Exception('To interpolate, must have at least one original y value to interpolate to')
    if not(origx.shape==origy.shape): 
        errormsg = 'To interpolate, original x and y vectors must be same length (x=%i, y=%i)' % (len(origx), len(origy))
        raise Exception(errormsg)
    
    # Make sure it's in the correct order
    correctorder = np.argsort(origx)
    origx = origx[correctorder]
    origy = origy[correctorder]
    neworder = argsort(newx)
    newx = newx[neworder] # And sort newx just in case
    
    # Only keep finite elements
    finitey = np.isfinite(origy) # Boolean for whether it's finite
    if finitey.any() and not finitey.all(): # If some but not all is finite, pull out indices that are
        finiteorigy = origy[finitey]
        finiteorigx = origx[finitey]
    else: # Otherwise, just copy the original
        finiteorigy = origy.copy()
        finiteorigx = origx.copy()
        
    # Perform actual interpolation
    if method=='linear':
        newy = np.interp(newx, finiteorigx, finiteorigy) # Perform standard interpolation without infinities
    elif method=='nearest':
        newy = np.zeros(newx.shape) # Create the new array of the right size
        for i,x in enumerate(newx): # Iterate over each point
            xind = np.argmin(abs(finiteorigx-x)) # Find the nearest neighbor
            newy[i] = finiteorigy[xind] # Copy it
    else:
        raise Exception('Method "%s" not found; methods are "linear" or "nearest"' % method)

    # Perform smoothing
    if smoothness is None: smoothness = np.ceil(len(newx)/len(origx)) # Calculate smoothness: this is consistent smoothing regardless of the size of the arrays
    smoothness = int(smoothness) # Make sure it's an appropriate number
    
    if smoothness:
        kernel = np.exp(-np.linspace(-2,2,2*smoothness+1)**2)
        kernel /= kernel.sum()
        validinds = findinds(~np.isnan(newy)) # Remove nans since these don't exactly smooth well
        if len(validinds): # No point doing these steps if no non-nan values
            validy = newy[validinds]
            prepend = validy[0]*np.ones(smoothness)
            postpend = validy[-1]*np.ones(smoothness)
            if not keepends:
                try: # Try to compute slope, but use original prepend if it doesn't work
                    dyinitial = (validy[0]-validy[1])
                    prepend = validy[0]*np.ones(smoothness) + dyinitial*np.arange(smoothness,0,-1)
                except:
                    pass
                try: # Try to compute slope, but use original postpend if it doesn't work
                    dyfinal = (validy[-1]-validy[-2])
                    postpend = validy[-1]*np.ones(smoothness) + dyfinal*np.arange(1,smoothness+1,1)
                except:
                    pass
            validy = np.concatenate([prepend, validy, postpend])
            validy = np.convolve(validy, kernel, 'valid') # Smooth it out a bit
            newy[validinds] = validy # Copy back into full vector
    
    # Apply growth if required
    if growth is not None:
        pastindices = findinds(newx<origx[0])
        futureindices = findinds(newx>origx[-1])
        if len(pastindices): # If there are past data points
            firstpoint = pastindices[-1]+1
            newy[pastindices] = newy[firstpoint] * np.exp((newx[pastindices]-newx[firstpoint])*growth) # Get last 'good' data point and apply inverse growth
        if len(futureindices): # If there are past data points
            lastpoint = futureindices[0]-1
            newy[futureindices] = newy[lastpoint] * np.exp((newx[futureindices]-newx[lastpoint])*growth) # Get last 'good' data point and apply growth
    
    # Add infinities back in, if they exist
    if any(~np.isfinite(origy)): # Infinities exist, need to add them back in manually since interp can only handle nan
        if not ensurefinite: # If not ensuring all entries are finite, put nonfinite entries back in
            orignan      = np.zeros(len(origy)) # Start from scratch
            origplusinf  = np.zeros(len(origy)) # Start from scratch
            origminusinf = np.zeros(len(origy)) # Start from scratch
            orignan[np.isnan(origy)]     = np.nan  # Replace nan entries with nan
            origplusinf[origy==np.inf]   = np.nan  # Replace plus infinite entries with nan
            origminusinf[origy==-np.inf] = np.nan  # Replace minus infinite entries with nan
            newnan      = np.interp(newx, origx, orignan) # Interpolate the nans
            newplusinf  = np.interp(newx, origx, origplusinf) # ...again, for positive
            newminusinf = np.interp(newx, origx, origminusinf) # ...and again, for negative
            newy[np.isnan(newminusinf)] = -np.inf # Add minus infinity back in first
            newy[np.isnan(newplusinf)]  = np.inf # Then, plus infinity
            newy[np.isnan(newnan)]  = np.nan # Finally, the nans
    
    # Restore original sort order for newy
    restoredorder = argsort(neworder)
    newy = newy[restoredorder]
    
    return newy
    

def perturb(n=1, span=0.5, randseed=None):
    ''' Define an array of numbers uniformly perturbed with a mean of 1. n = number of points; span = width of distribution on either side of 1.'''
    if randseed is not None: np.random.seed(int(randseed)) # Optionally reset random seed
    output = 1. + 2*span*(np.random.rand(n)-0.5)
    return output
    
    
def scaleratio(inarray,total):
    ''' Multiply a list or array by some factor so that its sum is equal to the total. '''
    origtotal = float(sum(inarray))
    ratio = total/origtotal
    outarray = np.array(inarray)*ratio
    if type(inarray)==list: outarray = outarray.tolist() # Preserve type
    return outarray


def vec2obj(orig=None, newvec=None, inds=None):
    ''' 
    Function to convert an e.g. budget/coverage vector into an e.g. budget/coverage odict ...or anything, really
    
    WARNING: is all the error checking really necessary?
    
    inds can be a list of indexes, or a list of keys, but newvec must be a list, array, or odict.
    
    Version: 2016feb04
    '''
    # Validate input
    if orig   is None: raise Exception('vec2obj() requires an original object to update')
    if newvec is None: raise Exception('vec2obj() requires a vector as input')
    lenorig = len(orig)
    lennew  = len(newvec)
    if lennew!=lenorig and inds is None: raise Exception('vec2obj(): if inds is not supplied, lengths must match (orig=%i, new=%i)' % (lenorig, lennew))
    if inds is not None and max(inds)>=len(orig): 
        raise Exception('vec2obj(): maximum index is greater than the length of the object (%i, %i)' % (max(inds), len(orig)))
    if inds is None: inds = range(lennew)

    # The actual meat of the function
    new = dcp(orig)    
    for i,ind in enumerate(inds):
        new[ind] = newvec[i]
    
    return new


def inclusiverange(*args, **kwargs):
    '''
    Like arange/linspace, but includes the start and stop points. 
    Accepts 0-3 args, or the kwargs start, stop, step. Examples:
    
    x = inclusiverange(3,5,0.2)
    x = inclusiverange(stop=5)
    x = inclusiverange(6, step=2)
    '''
    
    # Handle args
    if len(args)==0:
        start, stop, step = None, None, None
    elif len(args)==1:
        stop = args[0]
        start, step = None
    elif len(args)==2:
        start = args[0]
        stop   = args[1]
        step = None
    elif len(args)==3:
        start = args[0]
        stop = args[1]
        step = args[2]
    else:
        raise Exception('Too many arguments supplied: inclusiverange() accepts 0-3 arguments')
    
    # Handle kwargs
    start = kwargs.get('start', start)
    stop  = kwargs.get('stop',  stop)
    step  = kwargs.get('step',  step)
    
    # Finalize defaults
    if start is None: start = 0
    if stop  is None: stop  = 1
    if step  is None: step  = 1
    
    # OK, actually generate
    x = np.linspace(start, stop, int(round((stop-start)/float(step))+1)) # Can't use arange since handles floating point arithmetic badly, e.g. compare arange(2000, 2020, 0.2) with arange(2000, 2020.2, 0.2)
    
    return x




##############################################################################
### FILE/MISC. FUNCTIONS
##############################################################################


def saveobj(filename=None, obj=None, compresslevel=5, verbose=True, folder=None, method='pickle'):
    '''
    Save an object to file -- use compression 5 by default, since more is much slower but not much smaller.
    Once saved, can be loaded with loadobj() (q.v.).

    Usage:
		myobj = ['this', 'is', 'a', 'weird', {'object':44}]
		saveobj('myfile.obj', myobj)
    '''
    
    def savepickle(fileobj, obj):
        ''' Use pickle to do the salty work '''
        if _PY2: import cPickle as pickle # For Python 3 compatibility
        else:    import pickle
        fileobj.write(pickle.dumps(obj, protocol=-1))
        return None
    
    def savedill(fileobj, obj):
        ''' Use dill to do the sour work '''
        import dill
        fileobj.write(dill.dumps(obj, protocol=-1))
        return None
    
    from gzip import GzipFile
    fullpath = makefilepath(filename=filename, folder=folder, sanitize=True)
    with GzipFile(fullpath, 'wb', compresslevel=compresslevel) as fileobj:
        if method == 'dill': # If dill is requested, use that
            savedill(fileobj, obj)
        else: # Otherwise, try pickle
            try:    savepickle(fileobj, obj) # Use pickle
            except: savedill(fileobj, obj) # ...but use Dill if that fails
        
    if verbose: print('Object saved to "%s"' % fullpath)
    return fullpath


def loadobj(filename=None, folder=None, verbose=True):
    '''
    Load a saved file.

    Usage:
    	obj = loadobj('myfile.obj')
    '''
    if _PY2: import cPickle as pickle # For Python 3 compatibility
    else:    import pickle
    from gzip import GzipFile
    
    # Handle loading of either filename or file object
    if isinstance(filename, _stringtype): 
        argtype = 'filename'
        filename = makefilepath(filename=filename, folder=folder) # If it is a file, validate the folder
    else: 
        argtype = 'fileobj'
    kwargs = {'mode': 'rb', argtype: filename}
    with GzipFile(**kwargs) as fileobj:
        filestr = fileobj.read() # Convert it to a string
        try: # Try pickle first
            obj = pickle.loads(filestr) # Actually load it
        except:
            import dill
            obj = dill.loads(filestr)
    if verbose: print('Object loaded from "%s"' % filename)
    return obj


def loadtext(filename=None, splitlines=False):
    ''' Convenience function for reading a text file '''
    with open(filename) as f: output = f.read()
    if splitlines: output = output.splitlines()
    return output


def savetext(filename=None, string=None):
    ''' Convenience function for reading a text file -- accepts a string or list of strings '''
    if isinstance(string, list): string = '\n'.join(string) # Convert from list to string)
    with open(filename, 'w') as f: f.write(string)
    return None


def tic():
    '''
    A little pair of functions to calculate a time difference, sort of like Matlab:
    tic() [but you can also use the form t = tic()]
    toc() [but you can also use the form toc(t) where to is the output of tic()]
    '''
    global tictime  # The saved time is stored in this global.    
    from time import time
    tictime = time()  # Store the present time in the global.
    return tictime    # Return the same stored number.



def toc(start=None, label=None, sigfigs=None, filename=None, output=False):
    '''
    A little pair of functions to calculate a time difference, sort of like Matlab:
    tic() [but you can also use the form t = tic()]
    toc() [but you can also use the form toc(t) where to is the output of tic()]
    '''   
    from time import time
    
    # Set defaults
    if label   is None: label = ''
    if sigfigs is None: sigfigs = 3
    
    # If no start value is passed in, try to grab the global tictime.
    if start is None:
        try:    start = tictime
        except: start = 0 # This doesn't exist, so just leave start at 0.
            
    # Get the elapsed time in seconds.
    elapsed = time() - start
    
    # Create the message giving the elapsed time.
    if label=='': base = 'Elapsed time: '
    else:         base = 'Elapsed time for %s: ' % label
    logmessage = base + '%s s' % sigfig(elapsed, sigfigs=sigfigs)
    
    if output:
        return elapsed
    else:
        if filename is not None: printtologfile(logmessage, filename) # If we passed in a filename, append the message to that file.
        else: print(logmessage) # Otherwise, print the message.
        return None
    


def percentcomplete(step=None, maxsteps=None, indent=1):
    ''' Display progress '''
    onepercent = max(1,round(maxsteps/100)); # Calculate how big a single step is -- not smaller than 1
    if not step%onepercent: # Does this value lie on a percent
        thispercent = round(step/maxsteps*100) # Calculate what percent it is
        print('%s%i%%\n'% (' '*indent, thispercent)) # Display the output
    return None



def checkmem(origvariable, descend=0, order='n', plot=False, verbose=0):
    '''
    Checks how much memory the variable in question uses by dumping it to file.
    
    Example:
        from utils import checkmem
        checkmem(['spiffy',rand(2483,589)],descend=1)
    '''
    from os import getcwd, remove
    from os.path import getsize
    if _PY2: from cPickle import dump
    else:    from pickle import dump
    
    filename = getcwd()+'/checkmem.tmp'
    
    def dumpfile(variable):
        wfid = open(filename,'wb')
        dump(variable, wfid)
        return None
    
    printnames = []
    printbytes = []
    printsizes = []
    varnames = []
    variables = []
    if descend==False or not(np.iterable(origvariable)):
        varnames = ['']
        variables = [origvariable]
    elif descend==1 and np.iterable(origvariable):
        if hasattr(origvariable,'keys'):
            for key in origvariable.keys():
                varnames.append(key)
                variables.append(origvariable[key])
        else:
            varnames = range(len(origvariable))
            variables = origvariable
    
    for v,variable in enumerate(variables):
        if verbose: print('Processing variable %i of %i' % (v+1, len(variables)))
        dumpfile(variable)
        filesize = getsize(filename)
        factor = 1
        label = 'B'
        labels = ['KB','MB','GB']
        for i,f in enumerate([3,6,9]):
            if filesize>10**f:
                factor = 10**f
                label = labels[i]
        printnames.append(varnames[v])
        printbytes.append(filesize)
        printsizes.append('%0.3f %s' % (float(filesize/float(factor)), label))
        remove(filename)

    if order=='a' or order=='alpha' or order=='alphabetical':
        inds = np.argsort(printnames)
    else:
        inds = np.argsort(printbytes)

    for v in inds:
        print('Variable %s is %s' % (printnames[v], printsizes[v]))

    if plot==True:
        from pylab import pie, array, axes
        axes(aspect=1)
        pie(array(printbytes)[inds], labels=array(printnames)[inds], autopct='%0.2f')

    return None



def getfilelist(folder=None, ext=None, pattern=None):
    ''' A short-hand since glob is annoying '''
    from glob import glob
    import os
    if folder is None: folder = os.getcwd()
    if pattern is None:
        if ext is None: ext = '*'
        pattern = '*.'+ext
    filelist = sorted(glob(os.path.join(folder, pattern)))
    return filelist



def sanitizefilename(rawfilename):
    '''
    Takes a potentially Linux- and Windows-unfriendly candidate file name, and 
    returns a "sanitized" version that is more usable.
    '''
    import re # Import regular expression package.
    filtername = re.sub('[\!\?\"\'<>]', '', rawfilename) # Erase certain characters we don't want at all: !, ?, ", ', <, >
    filtername = re.sub('[:/\\\*\|,]', '_', filtername) # Change certain characters that might be being used as separators from what they were to underscores: space, :, /, \, *, |, comma
    return filtername # Return the sanitized file name.



def makefilepath(filename=None, folder=None, ext=None, default=None, split=False, abspath=True, makedirs=True, verbose=False, sanitize=False):
    '''
    Utility for taking a filename and folder -- or not -- and generating a valid path from them.
    
    Inputs:
        filename = the filename, or full file path, to save to -- in which case this utility does nothing
        folder = the name of the folder to be prepended to the filename
        ext = the extension to ensure the file has
        default = a name or list of names to use if filename is None
        split = whether to return the path and filename separately
        makedirs = whether or not to make the folders to save into if they don't exist
        verbose = how much detail to print
    
    Example:
        makefilepath(filename=None, folder='./congee', ext='prj', default=[project.filename, project.name], split=True, abspath=True, makedirs=True)
    
    Assuming project.filename is None and project.name is "soggyrice" and ./congee doesn't exist:
        * Makes folder ./congee
        * Returns e.g. ('/home/optima/congee', 'soggyrice.prj')
    
    Actual code example from project.py:
        fullpath = makefilepath(filename=filename, folder=folder, default=[self.filename, self.name], ext='prj')
    
    Version: 2017apr04    
    '''
    
    # Initialize
    import os
    filefolder = '' # The folder the file will be located in
    filebasename = '' # The filename
    
    # Process filename
    if filename is None:
        defaultnames = promotetolist(default) # Loop over list of default names
        for defaultname in defaultnames:
            if not filename and defaultname: filename = defaultname # Replace empty name with default name
    if filename is not None: # If filename exists by now, use it
        filebasename = os.path.basename(filename)
        filefolder = os.path.dirname(filename)
    if not filebasename: filebasename = 'default' # If all else fails
    
    # Add extension if it's defined but missing from the filebasename
    if ext and not filebasename.endswith(ext): 
        filebasename += '.'+ext
    if verbose:
        print('From filename="%s", default="%s", extension="%s", made basename "%s"' % (filename, default, ext, filebasename))
    
    # Sanitize base filename
    if sanitize: filebasename = sanitizefilename(filebasename)
    
    # Process folder
    if folder is not None: # Replace with specified folder, if defined
        filefolder = folder 
    if abspath: # Convert to absolute path
        filefolder = os.path.abspath(filefolder) 
    if makedirs: # Make sure folder exists
        try: os.makedirs(filefolder)
        except: pass
    if verbose:
        print('From filename="%s", folder="%s", abspath="%s", makedirs="%s", made folder name "%s"' % (filename, folder, abspath, makedirs, filefolder))
    
    fullfile = os.path.join(filefolder, filebasename) # And the full thing
    
    if split: return filefolder, filebasename
    else:     return fullfile # Or can do os.path.split() on output


def loadbalancer(maxload=None, index=None, interval=None, maxtime=None, label=None, verbose=True):
    '''
    A little function to delay execution while CPU load is too high -- a very simple load balancer.

    Arguments:
        maxload:  the maximum load to allow for the task to still start (default 0.5)
        index:    the index of the task -- used to start processes asynchronously (default None)
        interval: the time delay to poll to see if CPU load is OK (default 5 seconds)
        maxtime:  maximum amount of time to wait to start the task (default 36000 seconds (10 hours))
        label:    the label to print out when outputting information about task delay or start (default None)
        verbose:  whether or not to print information about task delay or start (default True)

    Usage examples:
        loadbalancer() # Simplest usage -- delay while load is >50%
        for nproc in processlist: loadbalancer(maxload=0.9, index=nproc) # Use a maximum load of 90%, and stagger the start by process number

    Version: 2017oct25
     '''
    from psutil import cpu_percent
    from time import sleep
    
    # Set up processes to start asynchronously
    if maxload  is None: maxload = 0.8
    if interval is None: interval = 5.0
    if maxtime  is None: maxtime = 36000
    if label    is None: label = ''
    else: label += ': '
    if index is None:  
        pause = np.random.rand()*interval
        index = ''
    else:              
        pause = index*interval
    if maxload>1: maxload/100. # If it's >1, assume it was given as a percent
    sleep(pause) # Give it time to asynchronize
    
    # Loop until load is OK
    toohigh = True # Assume too high
    count = 0
    maxcount = maxtime/float(interval)
    while toohigh and count<maxcount:
        count += 1
        currentload = cpu_percent(interval=0.1)/100. # If interval is too small, can give very inaccurate readings
        if currentload>maxload:
            if verbose: print(label+'CPU load too high (%0.2f/%0.2f); process %s queued %i times' % (currentload, maxload, index, count))
            sleep(interval*2*np.random.rand()) # Sleeps for an average of refresh seconds, but do it randomly so you don't get locking
        else: 
            toohigh = False 
            if verbose: print(label+'CPU load fine (%0.2f/%0.2f), starting process %s after %i tries' % (currentload, maxload, index, count))
    return None
    
    

def runcommand(command, printinput=False, printoutput=False):
   '''
   Make it easier to run shell commands.
   
   Date: 2018mar28
   '''
   from subprocess import Popen, PIPE
   if printinput: print(command)
   try:    output = Popen(command, shell=True, stdout=PIPE).communicate()[0].decode("utf-8")
   except: output = 'Shell command failed'
   if printoutput: print(output)
   return output



def gitinfo(filepath=None, die=False, hashlen=7):
    ''' Try to extract git information based on the file structure '''
    from os import path, sep # Path and file separator
    if filepath is None: filepath = __file__
    try: # First try importing git-python
        import git
        rootdir = path.abspath(filepath) # e.g. /user/username/optima/optima
        repo = git.Repo(path=rootdir, search_parent_directories=True)
        gitbranch = flexstr(repo.active_branch.name) # Just make sure it's a string
        githash = flexstr(repo.head.object.hexsha) # Unicode by default
        gitdate = flexstr(repo.head.object.authored_datetime.isoformat())
    except Exception as E1: 
        try: # If that fails, try the command-line method
            rootdir = path.abspath(filepath) # e.g. /user/username/optima/optima
            while len(rootdir): # Keep going as long as there's something left to go
                gitdir = rootdir+sep+'.git' # look for the git directory in the current directory
                if path.isdir(gitdir): break # It's found! terminate
                else: rootdir = sep.join(rootdir.split(sep)[:-1]) # Remove the last directory and keep looking
            headstrip = 'ref: ref'+sep+'heads'+sep # Header to strip off...hope this is generalizable!
            with open(gitdir+sep+'HEAD') as f: gitbranch = f.read()[len(headstrip)+1:].strip() # Read git branch name
            with open(gitdir+sep+'refs'+sep+'heads'+sep+gitbranch) as f: githash = f.read().strip() # Read git commit
            try:    gitdate = flexstr(runcommand('cd %s; git show -s --format=%%ci' % gitdir).rstrip()) # Even more likely to fail
            except: gitdate = 'Git date N/A'
        except Exception as E2: # Failure? Give up
            gitbranch = 'Git branch N/A'
            githash = 'Git hash N/A'
            gitdate = 'Git date N/A'
            if die:
                errormsg = 'Could not extract git info; please check paths or install git-python:\n%s\n%s' % (repr(E1), repr(E2))
                raise Exception(errormsg)
    
    if len(githash)>hashlen: githash = githash[:hashlen] # Trim hash to short length
    output = {'branch':gitbranch, 'hash':githash, 'date':gitdate} # Assemble outupt
    return output



def compareversions(version1=None, version2=None):
    '''
    Function to compare versions, expecting both arguments to be a string of the 
    format 1.2.3, but numeric works too.
    
    Usage:
        compareversions('1.2.3', '2.3.4') # returns -1
        compareversions(2, '2.0.0.0') # returns 0
        compareversions('3.1', '2.99') # returns 1
    
    '''
    if version1 is None or version2 is None: 
        raise Exception('Must supply both versions as strings')
    versions = [version1, version2]
    for i in range(2):
        versions[i] = np.array(flexstr(versions[i]).split('.'), dtype=float) # Convert to array of numbers
    maxlen = max(len(versions[0]), len(versions[1]))
    versionsarr = np.zeros((2,maxlen))
    for i in range(2):
        versionsarr[i,:len(versions[i])] = versions[i]
    for j in range(maxlen):
        if versionsarr[0,j]<versionsarr[1,j]: return -1
        if versionsarr[0,j]>versionsarr[1,j]: return 1
    if (versionsarr[0,:]==versionsarr[1,:]).all(): return 0
    else:
        raise Exception('Failed to compare %s and %s' % (version1, version2))





##############################################################################
### NESTED DICTIONARY FUNCTIONS
##############################################################################

'''
Four little functions to get and set data from nested dictionaries. The first two were stolen from:
    http://stackoverflow.com/questions/14692690/access-python-nested-dictionary-items-via-a-list-of-keys

"getnested" will get the value for the given list of keys:
    getnested(foo, ['a','b'])

"setnested" will set the value for the given list of keys:
    setnested(foo, ['a','b'], 3)

"makenested" will recursively update a dictionary with the given list of keys:
    makenested(foo, ['a','b'])

"iternested" will return a list of all the twigs in the current dictionary:
    twigs = iternested(foo)

Example 1:
    from nested import makenested, getnested, setnested
    foo = {}
    makenested(foo, ['a','b'])
    foo['a']['b'] = 3
    print getnested(foo, ['a','b'])    # 3
    setnested(foo, ['a','b'], 7)
    print getnested(foo, ['a','b'])    # 7
    makenested(foo, ['yerevan','parcels'])
    setnested(foo, ['yerevan','parcels'], 'were tasty')
    print foo['yerevan']  # {'parcels': 'were tasty'}

Example 2:
    from nested import makenested, iternested, setnested
    foo = {}
    makenested(foo, ['a','x'])
    makenested(foo, ['a','y'])
    makenested(foo, ['a','z'])
    makenested(foo, ['b','a','x'])
    makenested(foo, ['b','a','y'])
    count = 0
    for twig in iternested(foo):
        count += 1
        setnested(foo, twig, count)   # {'a': {'y': 1, 'x': 2, 'z': 3}, 'b': {'a': {'y': 4, 'x': 5}}}

Version: 2014nov29 
'''

def getnested(nesteddict, keylist, safe=False): 
    ''' Get a value from a nested dictionary'''
    from functools import reduce
    output = reduce(lambda d, k: d.get(k) if d else None if safe else d[k], keylist, nesteddict)
    return output

def setnested(nesteddict, keylist, value): 
    ''' Set a value in a nested dictionary '''
    getnested(nesteddict, keylist[:-1])[keylist[-1]] = value
    return None # Modify nesteddict in place

def makenested(nesteddict, keylist,item=None):
    ''' Insert item into nested dictionary, creating keys if required '''
    currentlevel = nesteddict
    for i,key in enumerate(keylist[:-1]):
        if not(key in currentlevel):
            currentlevel[key] = {}
        currentlevel = currentlevel[key]
    currentlevel[keylist[-1]] = item

def iternested(nesteddict,previous = []):
    output = []
    for k in nesteddict.items():
        if isinstance(k[1],dict):
            output += iternested(k[1],previous+[k[0]]) # Need to add these at the first level
        else:
            output.append(previous+[k[0]])
    return output


def flattendict(inputdict=None, basekey=None, subkeys=None, complist=None, keylist=None, limit=100):
    '''
    A function for flattening out a recursive dictionary, with an optional list of sub-keys (ignored if non-existent).
    The flattened out structure is returned as complist. Values can be an object or a list of objects.
    All keys (including basekey) within the recursion are returned as keylist.
    
    Specifically, this function is intended for dictionaries of the form...
        inputdict[key1][sub_key[0]] = [a, key2, b]
        inputdict[key1][sub_key[1]] = [c, d]
        inputdict[key2][sub_key[0]] = e
        inputdict[key2][sub_key[1]] = [e, f, g]
    ...which, for this specific example, will output list...
        [a, e, e, f, g, h, b, c, d]
        
    There is a max-depth of limit for the recursion.
    '''
    
    if limit<1:
        errormsg = 'ERROR: A recursion limit has been reached when flattening a dictionary, stopping at key "%s".' % basekey
        raise Exception(errormsg)    
    
    if complist is None: complist = []
    if keylist is None: keylist = []
    keylist.append(basekey)

    if subkeys is None: inputlist = inputdict[basekey]
    else:
        inputlist = []
        for sub_key in subkeys:
            if sub_key in inputdict[basekey]:
                val = inputdict[basekey][sub_key]
                if isinstance(val, list):
                    inputlist += val
                else:
                    inputlist.append(val)      # Handle unlisted objects.
    
    for comp in inputlist:
        if comp in inputdict.keys():
            flattendict(inputdict=inputdict, basekey=comp, subkeys=subkeys, complist=complist, keylist=keylist, limit=limit-1)
        else:
            complist.append(comp)
    return complist, keylist




##############################################################################
### PLOTTING FUNCTIONS
##############################################################################

def setylim(data=None, ax=None):
    '''
    A small script to determine how the y limits should be set. Looks
    at all data (a list of arrays) and computes the lower limit to
    use, e.g.
    
        setylim([array([-3,4]), array([6,4,6])], ax)
    
    will keep Matplotlib's lower limit, since at least one data value
    is below 0.
    
    Note, if you just want to set the lower limit, you can do that 
    with this function via:
        setylim(0, ax)
    '''
    # Get current limits
    currlower, currupper = ax.get_ylim()
    
    # Calculate the lower limit based on all the data
    lowerlim = 0
    upperlim = 0
    data = promotetolist(data) # Make sure it'siterable
    for ydata in data:
        lowerlim = min(lowerlim, promotetoarray(ydata).min())
        upperlim = max(upperlim, promotetoarray(ydata).max())
    
    # Set the new y limits
    if lowerlim<0: lowerlim = currlower # If and only if the data lower limit is negative, use the plotting lower limit
    upperlim = max(upperlim, currupper) # Shouldn't be an issue, but just in case...
    
    # Specify the new limits and return
    ax.set_ylim((lowerlim, upperlim))
    return lowerlim,upperlim


def SItickformatter(x, pos, sigfigs=2, SI=True, *args, **kwargs):  # formatter function takes tick label and tick position
    ''' Formats axis ticks so that e.g. 34,243 becomes 34K '''
    output = sigfig(x, sigfigs=sigfigs, SI=SI) # Pretty simple since sigfig() does all the work
    return output


def SIticks(fig=None, ax=None, axis='y'):
    ''' Apply SI tick formatting to one axis of a figure '''
    from matplotlib import ticker
    if  fig is not None: axlist = fig.axes
    elif ax is not None: axlist = promotetolist(ax)
    else: raise Exception('Must supply either figure or axes')
    for ax in axlist:
        if   axis=='x': thisaxis = ax.xaxis
        elif axis=='y': thisaxis = ax.yaxis
        elif axis=='z': thisaxis = ax.zaxis
        else: raise Exception('Axis must be x, y, or z')
        thisaxis.set_major_formatter(ticker.FuncFormatter(SItickformatter))
    return None


def commaticks(fig=None, ax=None, axis='y'):
    ''' Use commas in formatting the y axis of a figure -- see http://stackoverflow.com/questions/25973581/how-to-format-axis-number-format-to-thousands-with-a-comma-in-matplotlib '''
    from matplotlib import ticker
    if   ax  is not None: axlist = promotetolist(ax)
    elif fig is not None: axlist = fig.axes
    else: raise Exception('Must supply either figure or axes')
    for ax in axlist:
        if   axis=='x': thisaxis = ax.xaxis
        elif axis=='y': thisaxis = ax.yaxis
        elif axis=='z': thisaxis = ax.zaxis
        else: raise Exception('Axis must be x, y, or z')
        thisaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    return None



def boxoff(ax=None, removeticks=True, flipticks=True):
    '''
    I don't know why there isn't already a Matplotlib command for this.
    
    Removes the top and right borders of a plot. Also optionally removes
    the tick marks, and flips the remaining ones outside.

    Version: 2017may22    
    '''
    from pylab import gca
    if ax is None: ax = gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if removeticks:
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
    if flipticks:
        ax.tick_params(direction='out', pad=5)
    return ax




        



##############################################################################
### LINKS
##############################################################################


class LinkException(Exception):
        ''' An exception to raise when links are broken -- note, can't define classes inside classes :( '''
        def __init(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)


class Link(object):
    '''
    A class to differentiate between an object and a link to an object. Not very
    useful at the moment, but the idea eventually is that this object would be
    parsed differently from other objects -- most notably, a recursive method
    (such as a pickle) would skip over Link objects, and then would fix them up
    after the other objects had been reinstated.
    
    Version: 2017jan31
    '''
    
    def __init__(self, obj=None):
        ''' Store the reference to the object being referred to '''
        self.obj = obj # Store the object -- or rather a reference to it, if it's mutable
        try:    self.uid = obj.uid # If the object has a UID, store it separately 
        except: self.uid = None # If not, just use None
    
    
    def __repr__(self):
        ''' Just use default '''
        output  = desc(self)
        return output
    
    def __call__(self, obj=None):
        ''' If called with no argument, return the stored object; if called with argument, update object '''
        if obj is None:
            if type(self.obj)==LinkException: # If the link is broken, raise it now
                raise self.obj 
            return self.obj
        else:
            self.__init__(obj)
            return None
    
    def __copy__(self, *args, **kwargs):
        ''' Do NOT automatically copy link objects!! '''
        return Link(LinkException('Link object copied but not yet repaired'))
    
    def __deepcopy__(self, *args, **kwargs):
        ''' Same as copy '''
        return self.__copy__(self, *args, **kwargs)
        
        
