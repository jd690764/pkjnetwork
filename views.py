from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required

import time
# interactors handles the main 'node', 'edge','interaction', and 'dataSet' classes
from os import listdir
import re
from lib import networkMaker as nm
from lib import config as cf
import yaml
import os
import socket
import sys
from lib.markutils import tabulate
from numpy import percentile, unique
import lib.forms as fs

import logging
logger = logging.getLogger('django')

import pprint
pp = pprint.PrettyPrinter(indent=4)


def index(request):
    return HttpResponse("Hello - Please login first!")

@login_required()
def createNetwork( request ):
    files     = listdir(cf.djPath + 'data/nwfiles/')
    yamlfiles = dict()
    for f in files:
        if re.search( '^[^\.].*yaml$', f ):
            yamlfiles[f] = f
            
#    for k in yamlfiles:
#        print( k + ' ' + yamlfiles[k] )
    return render( request, 'network/createNetwork.html',  { 'yamlfiles' : sorted(yamlfiles.keys()) } )

@login_required()
def display( request ):
    t0    = time.time()
    fname = cf.djPath + 'data/nwfiles/' + request.POST['yaml']
    #print( 'fname=' + fname )
    nm.createNetwork( fname )

    with open( fname ) as infile :
        yout          = yaml.load(infile.read())

    outfile = yout['files'].get('outfile',None)

    choices = {}
    if os.path.isfile( cf.djPath + outfile ):
        outfile = cf.djpath + outfile

    if os.path.isfile( outfile ):
        with open( outfile ) as f:
            counter = 1
            for line in f:
                choices[ counter ] = line
                counter = counter + 1
                if counter > 11:
                    break

    outfilename = re.sub(r'^.*tmp/(.+)$', r'\1', outfile )
    t1          = time.time()
    time        = 'time it took: ' + str(t1 - t0)
    url         = '<a href="http://' + socket.gethostbyname(socket.gethostname()) + '/tmp/' + outfilename + '"> download .cyt file</a>'
    return render( request, 'network/display.html', { 'choices' : choices, 'url': url, 'time': time } )

@login_required()
def lookup( request ):

    result     = list()
    org        = None
    bait       = None
    symbol     = None
    
    if request.method == 'POST':

        org        = request.POST['org']
        bait       = request.POST.getlist('bait')
        symbol     = request.POST['symbol']
        siglist    = list()
    
        ifilenames = [fn for fn in os.listdir('/mnt/msrepo/ifiles') if fn[-2:] == '.i' and not 'bioplex' in fn and fn[0] != '.' ]
        baitl      = [ b.lower() for b in bait ]
        
        if not 'all' in bait:
            ifilenames = [fn for fn in ifilenames if fn.split('_')[0].lower() in baitl]
        
        if not org == 'all':
            ifilenames = [fn for fn in ifilenames if fn.split('_')[1] in org]
        
        for ifn in ifilenames :
            with open('/mnt/msrepo/ifiles/' + ifn) as ifile :
                for linel in tabulate(ifile) :
                    if linel[0].startswith('#') :
                        continue ;
                    elif linel[2].lower() == symbol.lower(): 
                        sig     = float(linel[3])
                        sc      = int( linel[9].split('_')[4])
                        length  = float( linel[9].split('_')[2])
                        siglist.append([ ifn, sig, sc, length ])
                        break
                    
        siglist = sorted( siglist, key=lambda x: x[1], reverse = True )
        
        for i in range(0,len(siglist)) :
            result.append( [ siglist[i][0], '(rank ' + str(i+1) + '/' + str(len(siglist)) + ' appearances)', '[{: <4.2E}]'.format( siglist[i][1]), siglist[i][2], siglist[i][3] ] )
            
    eform  = fs.lookupForm( initial={'org': 'all', 'bait': 'all'} )
    if org == '9606':
        org    = 'Human'
    elif org == '10090':
        org    = 'Mouse'
        
    return render( request, 'network/lookup.html', { 'form' : eform, 'choices': result, 'symbol': symbol, 'bait': bait, 'org': org })

