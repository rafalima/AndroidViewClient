#! /usr/bin/env monkeyrunner
'''
Copyright (C) 2013  Diego Torres Milano
Created on Mar 28, 2013

Scripter helps you create AndroidViewClient scripts generating a working template that can be
modified to suit more specific needs.

@author: diego
'''

__version__ = '0.9.0'

import re
import sys
import os
import getopt
import warnings
from datetime import date

# This must be imported before MonkeyRunner and MonkeyDevice,
# otherwise the import fails.
# PyDev sets PYTHONPATH, use it
try:
    for p in os.environ['PYTHONPATH'].split(':'):
        if not p in sys.path:
            sys.path.append(p)
except:
    pass
    
try:
    sys.path.append(os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

from com.dtmilano.android.viewclient import ViewClient

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
  
HELP = 'help'
VERBOSE = 'verbose'
IGNORE_SECURE_DEVICE = 'ignore-secure-device'
FORCE_VIEW_SERVER_USE = 'force-view-server-use'
DO_NOT_START_VIEW_SERVER = 'do-not-start-view-server'
FIND_VIEWS_BY_ID = 'find-views-by-id'
FIND_VIEWS_WITH_TEXT = 'find-views-with-text'
# -u,-s,-p,-v eaten by monkeyrunner
LONG_OPTS =  [HELP, VERBOSE, IGNORE_SECURE_DEVICE, FORCE_VIEW_SERVER_USE, DO_NOT_START_VIEW_SERVER,
              FIND_VIEWS_BY_ID, FIND_VIEWS_WITH_TEXT]
ID_RE = re.compile('id/([^/]*)(/(\d+))?')

def variableNameFromId(id):
    '''
    Returns a suitable variable name from the id.
    
    @type id: str
    @param id: the I{id}
    @return: the variable name from the id
    '''
    
    m = ID_RE.match(id)
    if m:
        var = m.group(1)
        if m.group(3):
            var += m.group(3)
        if re.match('^\d', var):
            var = 'id_' + var
        return var
    else:
        raise Exception('Not an id: %s' % id)

def traverseAndPrintFindViewById(view):
    '''
    Traverses the View tree and prints the corresponding statement.
    
    @type view: L{View}
    @param view: the View
    '''
    
    id = view.getUniqueId()
    var = variableNameFromId(id)
    try:
        print '# tag=%s' % view.getTag()
    except:
        pass
    print '%s = vc.findViewByIdOrRaise("%s")' % (var, id)

def traverseAndPrintFindViewWithText(view):
    '''
    Traverses the View tree and prints the corresponding statement.
    
    @type view: L{View}
    @param view: the View
    '''
    
    id = view.getUniqueId()
    text = view.getText()
    if text:
        var = variableNameFromId(id)
        print '%s = vc.findViewWithTextOrRaise("%s")' % (var, text)
    else:
        warnings.warn('View with id=%s has no text' % id)

def usage(exitVal=1):
    print >> sys.stderr, 'usage: scripter.py [-H|--%s] [-V|--%s] [-I|--%s] [-F|--%s] [-S|--%s] [-i|--%s] [-t|--%s] [serialno]' % \
        tuple(LONG_OPTS)
    sys.exit(exitVal)

try:
    opts, args = getopt.getopt(sys.argv[1:], 'HVIFSit', LONG_OPTS)
except getopt.GetoptError, e:
    print >>sys.stderr, 'ERROR:', str(e)
    usage()

kwargs1 = {VERBOSE: False, 'ignoresecuredevice': False}
kwargs2 = {'forceviewserveruse': False, 'startviewserver': True}
transform = traverseAndPrintFindViewById
for o, a in opts:
    o = o.strip('-')
    if o in ['H', HELP]:
        usage(0)
    elif o in ['V', VERBOSE]:
        kwargs1[VERBOSE] = True
    elif o in ['I', IGNORE_SECURE_DEVICE]:
        kwargs1['ignoresecuredevice'] = True
    elif o in ['F', FORCE_VIEW_SERVER_USE]:
        kwargs2['forceviewserveruse'] = True
    elif o in ['S', DO_NOT_START_VIEW_SERVER]:
        kwargs2['startviewserver'] = False
    elif o in ['i', FIND_VIEWS_BY_ID]:
        transform = traverseAndPrintFindViewById
    elif o in ['t', FIND_VIEWS_WITH_TEXT]:
        transform = traverseAndPrintFindViewWithText

device, serialno = ViewClient.connectToDeviceOrExit(**kwargs1)
vc = ViewClient(device, serialno, **kwargs2)
print '''#! /usr/bin/env monkeyrunner
\'\'\'
Copyright (C) 2013  Diego Torres Milano
Created on %s by Scripter
  
@author: diego
\'\'\'


import re
import sys
import os

# This must be imported before MonkeyRunner and MonkeyDevice,
# otherwise the import fails.
# PyDev sets PYTHONPATH, use it
try:
    for p in os.environ['PYTHONPATH'].split(':'):
        if not p in sys.path:
            sys.path.append(p)
except:
    pass
    
try:
    sys.path.append(os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

from com.dtmilano.android.viewclient import ViewClient

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
  
device, serialno = ViewClient.connectToDeviceOrExit()
vc = ViewClient(device, serialno)
''' % date.today()

vc.traverse(transform=transform)
