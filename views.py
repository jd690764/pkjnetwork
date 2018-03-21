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
from network.models import Sample, Preprocess
import pickle

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
    expt       = None
    cline      = None

    if request.method == 'POST':

        org        = request.POST['org']
        bait       = request.POST.getlist('bait')
        symbol     = request.POST['symbol']
        expt       = request.POST['expt']
        cline      = request.POST['cline']
        siglist    = list()
        use_regex  = True if re.search(r'\*', symbol) else False
        limit_to_one_dataset = False
        if re.search(r'.*\*.*', symbol):
            if re.search( r'^\*$', symbol) and 'all' in bait and expt == 'select one':
                limit_to_one_dataset = True

            sym_re = re.compile( '^' + re.sub(r'\*', r'.*', symbol), re.I )
        else:
            if org == 'all' and cline == 'all' and expt != 'select one':
                # we want to lookup mouse/human ortholog and search with both
                h2m = pickle.load(open(cf.filesDict['h2ms'], 'rb'))
                m2h = pickle.load(open(cf.filesDict['m2hs'], 'rb'))
                symbol_h = ''
                symbol_m = ''
                symbol_lower = symbol.lower()
                if symbol_lower in h2m:
                    symbol_h = h2m[symbol_lower][0]
                    symbol_m = '|'.join(h2m[symbol_lower][1])
                elif symbol_lower in m2h:
                    symbol_m = m2h[symbol_lower][0]
                    symbol_h = '|'.join(m2h[symbol_lower][1])

                if len(symbol_h) > 0 and len(symbol_m) > 0:
                    sym_re = re.compile( '^(' + symbol_h + '|' + symbol_m + ')', re.I )
                    symbol = 'Human: ' + symbol_h + ' -- Mouse: ' + symbol_m
                    use_regex = True
            #sym_re = re.compile( '^' + symbol, re.I )    
        samples    = Sample.objects.all()
        preprocess = Preprocess.objects.all()
        ifilenames = [fn for fn in os.listdir(cf.ifilesPath) if fn[-2:] == '.i' and not 'bioplex' in fn and fn[0] != '.' ]
        baitl      = [ b.lower() for b in bait ]
        
        if not expt == 'select one':
            ifilenames = [fn for fn in ifilenames if expt in fn] 
        else:
            if not 'all' in bait:
                #ifilenames = [fn for fn in ifilenames if fn.split('_')[0].lower() in baitl]
                samples = samples.filter(bait_symbol = bait)

            if not org == 'all':
                #ifilenames = [fn for fn in ifilenames if fn.split('_')[1] in org]
                samples = samples.filter(taxid = org)

            if not cline == 'all':
                samples = samples.filter(cell_line__contains=cline)

            samples    = samples.filter(display=True).filter(discard=False)
            sampleids  = samples.values('id')
            samplesMap = {d['id']: d['cell_line'] for d in samples.values('id', 'cell_line')}

            preprocess = preprocess.filter(sampleid__in=sampleids)
            pp_data    = preprocess.values('bait_symbol_eid', 'taxid', 'special', 'sampleid')
            # add cell lines to records
            for d in pp_data:
                d.update({'cell_line': samplesMap[d['sampleid']]})

            pp_files   = {'_'.join([re.sub(r'_\d+$', r'', d['bait_symbol_eid']), str(d['taxid']), str(d['special'])]): d['cell_line'] for d in pp_data}
            pp_files   = {re.sub('_None$', '', k): pp_files[k] for k in pp_files.keys()}
            ifiles     = [re.sub(r'_\d+\.i$', r'', f) for f in ifilenames]
            
            # these are the ifiles that remain after all the filtrations above
            ifilenames = {ifilenames[i]: pp_files[ifiles[i]] for i in [i for i, j in enumerate(ifiles) if j in pp_files.keys()]}

        def rowData( ifn, l, cl ):
            sig     = float(l[3])
            sc      = int( re.sub(r'.*_raw_(\d+)(_.+|$)', r'\1', l[9] ))
            length  = round(float( re.sub(r'.*_len_([\d\.]+)_.*', r'\1', l[9] )), 2)
            cov     = float( re.sub(r'.*_cov_([\d\.\-]+)_.*', r'\1', l[9] )) if re.search(r'_cov_', l[9] ) else -1
            upept   = int( re.sub(r'.*upept_([\d\-]+)$', r'\1', l[9] )) if re.search(r'_upept_', l[9] ) else -1
            prey    = l[2]
            celline = cl
            return( ifn, prey, sig, sc, length, cov, upept, celline )
            
        for ifn in ifilenames.keys() :
            with open(cf.ifilesPath + ifn) as ifile :
                for linel in tabulate(ifile) :
                    if linel[0].startswith('#') or linel[0].startswith('ID'):
                        continue ;
                    elif not use_regex and linel[2].lower() == symbol.lower():
                        siglist.append( list(rowData(ifn, linel, ifilenames[ifn])))
                        # if we are not using regex, don't allow multiple hits in same dataset
                        break
                    
                    elif use_regex and re.search( sym_re, linel[2] ) :
                        if linel[2] == 'PSEUDO':
                            continue

                        siglist.append( list(rowData(ifn, linel)))

            if limit_to_one_dataset:
                bait = ['__limited to__:' + ifn]
                break
                                    
                    
        siglist = sorted( siglist, key=lambda x: x[2], reverse = True )
        
        for i in range(0,len(siglist)) :
            result.append( [ siglist[i][0], siglist[i][1], '(rank ' + str(i+1) + '/' + str(len(siglist)) + ' appearances)', 
                             '{: <4.2E}'.format( siglist[i][2]), siglist[i][3], siglist[i][4], siglist[i][5], siglist[i][6], siglist[i][7] ] )
            
    eform  = fs.lookupForm( initial={'org': 'all', 'bait': 'all', 'expt': 'select one', 'cline': 'all'} )

    if org in orgDict:
        org = orgDict[ org ]    

    return render( request, 'network/lookup.html', { 'form' : eform, 'choices': result, 'symbol': symbol, 'bait': bait, 'org': org, 'expt': expt, 'cline': cline })

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
        ptm_dir      = cf.ptmsPath
        
        dirs       = [ x for x in os.listdir(ptm_dir)]

        baitl      = [ b.lower() for b in bait ]

        query      = Sample.objects.all()
        #query      = Sample.objects.filter(discard = False, display = True, ff_folder__isnull = False).values('uid').annotate(id = Max(id))
        
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
                    if linel[0].startswith('#') :
                        continue ;
                    elif linel[0] == 'dset':
                        header    = {k: v for v, k in enumerate(linel)}
                    elif linel[1].lower() == symbol.lower() and linel[3] == modification: 
                        dset      = linel[header['dset']]
                        descr     = linel[header['descr']]
                        resid     = linel[header['residue']]
                        pos       = int(linel[header['pos']])
                        mod_count = float( linel[header['mod_count']] )
                        all_count = float( linel[header['all_count']] )
                        print( dset + '+' + descr + '+' + resid + '+' + str(pos) + '+' + str(mod_count) + '+' + str(all_count))
                        siglist.append([ labels[dset], descr, resid, pos, mod_count, all_count, '{0:.2f}'.format(100 * mod_count/all_count) ])
                        #break
                    
        siglist = sorted( siglist, key=lambda x: (x[0], x[1], x[3]))
        result  = siglist
            
    eform  = fs.lookupPtmForm( initial={'org': 'all', 'bait': 'all', 'expt': 'all', 'modif': 'Phosphorylation'} )

    if org in orgDict:
        org = orgDict[ org ]
        
    return render( request, 'network/lookupPTM.html', { 'form' : eform, 'choices': result, 'symbol': symbol, 'bait': bait, 'org': org, 'expt': expt, 'mods': modification })

