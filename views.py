from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.db.models import Q 

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
from network.models import Sample

import logging
logger = logging.getLogger('django')

import pprint
pp = pprint.PrettyPrinter(indent=4)

orgDict = { '10090': 'mouse', '9606': 'human', 'all': 'all'}

def index(request):
    return HttpResponse("Hello - Please login first!")

@login_required()
def createNetwork( request ):
    files     = listdir(cf.djPath + 'data/nwfiles/')
    yamlfiles = dict()
    for f in files:
        if re.search( '^[^\.].*yaml$', f ):
            yamlfiles[f] = f
            
    return render( request, 'network/createNetwork.html',  { 'yamlfiles' : sorted(yamlfiles.keys()) } )

@login_required()
def display( request ):
    import time
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
        use_regex  = True if re.search(r'\*', symbol) else False
        limit_to_one_dataset = False
        if re.search(r'.*\*.*', symbol):
            if re.search( r'^\*$', symbol):
                limit_to_one_dataset = True

            symbol = symbol.lower()
            sym_re = re.compile( '^' + re.sub(r'\*', r'.*', symbol) )
        else:
            sym_re = re.compile( '^' + symbol )    
    
        ifilenames = [fn for fn in os.listdir('/mnt/msrepo/ifiles') if fn[-2:] == '.i' and not 'bioplex' in fn and fn[0] != '.' ]
        baitl      = [ b.lower() for b in bait ]
        
        if not 'all' in bait:
            ifilenames = [fn for fn in ifilenames if fn.split('_')[0].lower() in baitl]
        
        if not org == 'all':
            ifilenames = [fn for fn in ifilenames if fn.split('_')[1] in org]
        
        for ifn in ifilenames :
            with open('/mnt/msrepo/ifiles/' + ifn) as ifile :
                for linel in tabulate(ifile) :
                    if linel[0].startswith('#') or linel[0].startswith('ID'):
                        continue ;
                    #elif linel[2].lower() == symbol.lower():
                    elif re.search( sym_re, linel[2].lower()) :
                        if linel[2] == 'PSEUDO':
                            continue
                        sig     = float(linel[3])
                        sc      = int( re.sub(r'.*raw_(\d+)$', r'\1', linel[9] ))
                        length  = float( re.sub(r'.*_len_([\d\.]+)_raw.*', r'\1', linel[9] ))
                        prey    = linel[2]
                        siglist.append([ ifn, prey, sig, sc, length ])
                        if not use_regex:
                            # if we are not using regex, don't allow multiple hits in same dataset
                            break
            if limit_to_one_dataset:
                bait = ['__limited to__:' + ifn]
                break
                                    
                    
        siglist = sorted( siglist, key=lambda x: x[2], reverse = True )
        
        for i in range(0,len(siglist)) :
            result.append( [ siglist[i][0], siglist[i][1], '(rank ' + str(i+1) + '/' + str(len(siglist)) + ' appearances)', '[{: <4.2E}]'.format( siglist[i][2]), siglist[i][3], siglist[i][4] ] )
            
    eform  = fs.lookupForm( initial={'org': 'all', 'bait': 'all'} )

    if org in orgDict:
        org = orgDict[ org ]    

    return render( request, 'network/lookup.html', { 'form' : eform, 'choices': result, 'symbol': symbol, 'bait': bait, 'org': org })

@login_required()
def lookupPTM( request ):

    result       = list()
    org          = None
    bait         = None
    symbol       = None
    modification = None
    expt         = None
    
    if request.method == 'POST':

        org          = request.POST['org']
        bait         = request.POST.getlist('bait')
        symbol       = request.POST['symbol']
        expt         = request.POST['expt']
        modification = request.POST['modif']
        siglist      = list()
        dfilenames   = list()
        ptm_dir      = '/mnt/msrepo/fractionFiles/PTMs/'
        
        dirs       = [ x for x in os.listdir(ptm_dir)]

        baitl      = [ b.lower() for b in bait ]

        query      = Sample.objects.all()
        
        if not 'all' in bait:
            query  = query.filter(bait_symbol__in=bait)
        
        if not org == 'all':
            query  = query.filter(taxid = org )

        if not 'all' in expt:
            query  = query.filter(label=expt)

        query      = query.filter(ff_folder__isnull=False).filter(ff_folder__in=dirs)
        qresult    = query.values('ff_folder', 'label')
        to_search  = [ d['ff_folder'] for d in qresult]
        labels     = { d['ff_folder']: d['label'] for d in qresult}

        for d in to_search:
            try:
                dfilenames.append([ ptm_dir + d + '/' + f for f in os.listdir(ptm_dir + d) if re.search(r'^[a-zA-Z0-9].*mods_summary_data.tsv', f)][0])
            except IndexError:
                continue

        for dfn in dfilenames :
            if re.search(r'WT1', dfn):
                # some bad character in the file breaks it
                continue
            
            with open(dfn, 'rt') as dfile :
                for line in dfile:
                #for linel in tabulate(dfile) :
                    linel         = line.strip().split('\t')
                    print(linel[1] + '  ' + linel[3])
                    if linel[0].startswith('#') :
                        continue ;
                    elif linel[1].lower() == symbol.lower() and linel[3] == modification: 
                        dset      = linel[0]
                        descr     = linel[2]
                        resid     = linel[5]
                        pos       = int(linel[4])
                        mod_count = float( linel[6] )
                        all_count = float( linel[7] )
                        print( dset + '+' + descr + '+' + resid + '+' + str(pos) + '+' + str(mod_count) + '+' + str(all_count))
                        siglist.append([ labels[dset], descr, resid, pos, mod_count, all_count, '{0:.2f}'.format(100 * mod_count/all_count) ])
                        #break
                    
        siglist = sorted( siglist, key=lambda x: (x[0], x[1], x[3]))
        result  = siglist
            
    eform  = fs.lookupPtmForm( initial={'org': 'all', 'bait': 'all', 'expt': 'all', 'modif': 'Phosphorylation'} )

    if org in orgDict:
        org = orgDict[ org ]
        
    return render( request, 'network/lookupPTM.html', { 'form' : eform, 'choices': result, 'symbol': symbol, 'bait': bait, 'org': org, 'expt': expt, 'mods': modification })

