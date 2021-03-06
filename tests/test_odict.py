"""
Define a suite of tests for the odict
"""

import numpy as np
import sciris as sc

count = 0
def odprint(label):
    global count
    count += 1
    sc.colorize('blue', '\n%s. '%count+label)
    return None

def printexamples(examples):
    for v,val in enumerate(examples):
        print('Example %s:' % (v+1))
        print(val)
        print('')
    return None

odprint('Main tests:')
foo = sc.odict({'ah':3,'boo':4, 'cough':6, 'dill': 8}) # Create odict
bar = foo.sorted() # Sort the list
assert(bar['boo'] == 4) # Show get item by value
assert(sc.objdict(bar).boo == 4) # Show get item by value, method 2
assert(bar[1] == 4) # Show get item by index
assert((bar[0:2] == [3,4]).all()) # Show get item by slice
assert((bar['cough':'dill'] == [6,8]).all()) # Show alternate slice notation
assert((bar[np.array([2,1])] == [6,4]).all()) # Show get item by list
assert((bar[:] == [3,4,6,8]).all()) # Show slice with everything
assert((bar[2:] == [6,8]).all()) # Show slice without end
bar[3] = [3,4,5] # Show assignment by item
bar[0:2] = ['the', 'power'] # Show assignment by slice -- NOTE, inclusive slice!!
bar[[0,2]] = ['cat', 'trip'] # Show assignment by list
bar.rename('cough','chill') # Show rename
printexamples([foo,bar])

odprint('Insert:')
z = sc.odict()
z['foo'] = 1492
z.insert(1604)
z.insert(0, 'ganges', 1444)
z.insert(2, 'midway', 1234) 
printexamples([z])

odprint('Make:')
a = sc.odict().make(5) # Make an odict of length 5, populated with Nones and default key names
b = sc.odict().make('foo',34) # Make an odict with a single key 'foo' of value 34
c = sc.odict().make(['a','b']) # Make an odict with keys 'a' and 'b'
d = sc.odict().make(['a','b'],0) # Make an odict with keys 'a' and 'b', initialized to 0
e = sc.odict().make(keys=['a','b'], vals=[1,2]) # Make an odict with 'a':1 and 'b':2
f = sc.odict({'a':34, 'b':58}).make(['c','d'],[99,45]) # Add extra keys to an exising odict
g = sc.odict().make(keys=['a','b','c'], keys2=['A','B','C'], keys3=['x','y','z'], vals=0) # Make a triply nested odict
printexamples([a,b,c,d,e,f,g])

odprint('Make from:')
a = 'cat'; b = 'dog'; o = sc.odict().makefrom(source=locals(), keys=['a','b']) # Make use of fact that variables are stored in a dictionary
d = {'a':'cat', 'b':'dog'}; p = sc.odict().makefrom(d) # Same as sc.odict(d)
l = ['cat', 'monkey', 'dog']; q = sc.odict().makefrom(source=l, keys=[0,2], keynames=['a','b'])
printexamples([o,p,q])


odprint('Map:')
cat = sc.odict({'a':[1,2], 'b':[3,4]})
def myfunc(mylist): return [i**2 for i in mylist]
dog = cat.map(myfunc) # Returns sc.odict({'a':[1,4], 'b':[9,16]})
printexamples([cat, dog])

odprint('From each:')
z = sc.odict({'a':np.array([1,2,3,4]), 'b':np.array([5,6,7,8])})
f = z.fromeach(2) # Returns array([3,7])
g = z.fromeach(ind=[1,3], asdict=True) # Returns sc.odict({'a':array([2,4]), 'b':array([6,8])})
printexamples([f,g])

odprint('To each:')
z = sc.odict({'a':[1,2,3,4], 'b':[5,6,7,8]})
z.toeach(2, [10,20])    # z is now sc.odict({'a':[1,2,10,4], 'b':[5,6,20,8]})
z.toeach(ind=3,val=666) #  z is now sc.odict({'a':[1,2,10,666], 'b':[5,6,20,666]})
printexamples([z])

odprint('Findkeys, findbykey, and findvals:')
yy = sc.odict({'foo':[1,2,3,4], 'bar':[5,6,7,8], ('cat','dog'):[5,6,7,8]})
print(yy.findkeys()) # Equivalent to yy.keys()
print(yy.findkeys('oo'))
print(yy.findkeys('^oo'))
print(yy.findkeys('oo', method='endswith'))
print(yy.findkeys('cat'))
print(yy.findbykey('ar'))
print(yy.findbyval([5,6,7,8]))
a = yy.filter('a')
b = yy.filter('a', exclude=True)
c = yy.filter(['foo', 'bar'])
d = yy.filtervals([1,2,3,4])
printexamples([a,b,c,d])




print('Done.')
