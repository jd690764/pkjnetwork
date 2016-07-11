#!/usr/env/python -c
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from network.models import Entrez
from fileUtils import read_config

import interactors as I
import interactors_extras as ie
import rbase

import argparse
import sys
import os
from os import listdir
from io import StringIO
import colorama
import numpy as np
deprecation=colorama.Fore.RED+" DEPRECATED 21 APRIL 2016 "+colorama.Fore.RESET

# kludge for temporary disabling of interactive mode

def index( request ):
    return render( request, 'network/index.html', {} )

def display( request ):

    conf = read_config( sys.argv[1] )


            
    def tokey(s) :
        return s+'_'+rbase.hmg['Symbol'][s]['EID'] ; 

    theds=I.dataSet(n_filter=ie.bg_regex_assembler()[1]) ;

    if 'm2h' in [ d.get('convert') for d in ds_dicts ] : 
        rbase.load('m2h') ; 

    if 'h2m' in [ d.get('convert') for d in ds_dicts ] : 
        rbase.load('h2m') ; 


# parse datasets
baitkeys=list() ; 
# iterating through the dataset items
for dsd in ds_dicts : 

    if dsd['infilename'] in os.listdir('.') : 
        dsf=open(dsd['infilename']) ; 
    else : 
        dsf=open('/mnt/msrepo/ifiles/'+dsd['infilename']) ; 

    if dsd.get('convert') == 'm2h' : 
        theds.parse(dsf,fd=I.fdms,m2h=True,qualify=dsd.get('qualify',''),directed=True) ; 
    elif dsd.get('convert') == 'h2m' : 
        theds.parse(dsf,fd=I.fdms,h2m=True,qualify=dsd.get('qualify',''),directed=True) ; 
    else : 
        theds.parse(dsf,fd=I.fdms,qualify=dsd.get('qualify',''),directed=True) ; 

    baitkeys.append(tokey(dsd['bait'])) ; 

    dsf.close() ; 

panel_dsses=list()
# list of lists
panel_baits=list() ;

zfhits_strong=set() ;
zfhits_weak=set() ;
for dsd in ds_dicts : 
    zfhits_strong |= ie.madfilter(theds,dsd['control'],tokey(dsd['bait']),\
     qual=dsd.get('qualify'),directed=True,alpha=ALPHA_HI)
    zfhits_weak |= ie.madfilter(theds,dsd['control'],tokey(dsd['bait']),\
     qual=dsd.get('qualify'),directed=True,alpha=ALPHA_LO)

zfhits_joint = zfhits_strong | zfhits_weak

# pass 1 nodes : every node at the end of one of the validated edges
node_pass1_all={ nk for ek in zfhits_joint for nk in {theds.edges[ek].to.key,theds.edges[ek].whence.key}} ; 
node_pass1_strong={ nk for ek in zfhits_strong for nk in {theds.edges[ek].to.key,theds.edges[ek].whence.key}}
edges_pass1=set() ; 

# read the rescue file
if rescue_f : 
    rescued=set(rescue_f.read().splitlines())  ;
    rescue_f.close() ;
else : 
    rescued={}

# OK, NOW we dump in the public datasets
for pd in public_dicts :
    # (done) make emili follow biogrid field conventions
    # TODO ditto bioplex
    if pd['infilename'] in os.listdir('.') : 
        pdsf=open(dsd['infilename']) ; 
    elif os.path.isfile(pd['infilename']) :
        pdsf=open(pd['infilename']) ; 
    else : 
        pdsf=open('/mnt/reference'+pd['infilename']) ; 

    temporaryds=I.dataSet(i_filter=ie.bg_regex_assembler()[0])
    if pd.get('convert') == 'm2h' : 
        temporaryds.parse(pdsf,fd=I.fd_biogrid,m2h=True,qualify=pd.get('qualify',''),directed=True,force_qualify=True) ; 
    elif pd.get('convert') == 'h2m' : 
        temporaryds.parse(pdsf,fd=I.fd_biogrid,h2m=True,qualify=pd.get('qualify',''),directed=True,force_qualify=True) ; 
    else : 
        temporaryds.parse(pdsf,fd=I.fd_biogrid,qualify=pd.get('qualify',''),directed=True,force_qualify=True) ; 

    sio=StringIO() ;
    temporaryds.save(sio,edges={ e for e in temporaryds.edges.values() \
     if e.weight >= pd.get('minweight',0) and e.totalscore > pd.get('minscore',0)} );
    sio.seek(0)
    theds.load_from(sio) ;
    sio.close() ;

    pdsf.close() ; 

reinforcing_edges=set() ; 
# public edges used to evaluate binding to baits

# pass 1 edges include if ...:
# this filtration will now be taken care of above, immediately after 
#parsing
for e in list(theds.edges.values()) : 
    if e.key in zfhits_joint : 
        # passed filtering
        edges_pass1.add(e) ; 
    elif {e.to.key,e.whence.key}.issubset(node_pass1_all) : 
        edges_pass1.add(e) ; 
        reinforcing_edges.add(e) ; 

# network-wide degree rescue
# this block puts all edges with appropriate quals in the 
# valid_qual_edges set, which will be used to calculate degrees
# if NWD is true. Otherwise this set needs to be recreated
# depending on which baits a protein binds
if nwd : 
    if valid_quals == 'default' : 
        vqe={ e.key for e in theds.edges.values() if e.qual not in {'bg','bp'} } ;
    elif valid_quals == 'all' : 
        vqe={ e.key for e in theds.edges.values()} ;
    elif type(valid_quals) is set : 
        vqe={ e.key for e in theds.edges.values() if e.qual in valid_quals }; 
else : 
    vqe=set() ;

nodes_pass2=set() ; 

nnodes_rescued = 0

#RESUME
for nk in node_pass1_all : 

    if nk in node_pass1_strong : 
        nodes_pass2.add(nk) ;
    elif any([ theds.nodes[nk].binds(bk,within_edge_set=reinforcing_edges) and \
         theds.nodes[nk].binds(bk,within_edge_set=zfhits_joint) 
         for bk in baitkeys ]) : 
        # if node keyed by nk binds bait bk with both a publicly recognized edge and
        # an observed weak edge, make sure that node stays
        nodes_pass2.add(nk) ;
    elif not nwd : 
        edges_this_node={ e.key for es in theds.nodes[nk].edges.values() for e in es }\
         & ( edges_pass1 | reinforcing_edges ); 
        # possibly ok edges

        if valid_quals == 'default' : 
            vqe={ e.key for e in edges_this_node if e.qual not in {'bg','bp'} } ;
        elif valid_quals == 'all' : 
            vqe={ e.key for e in edges_this_node } ;
        elif type(valid_quals) is set : 
            vqe={ e.key for e in edges_this_node if e.qual in valid_quals }; 
        else : 
            vqe=set() ;

        for bk in baitkeys : 
            partners_this_node={ n for n in theds.nodes[nk].partners.values() if\
                                 theds.nodes[nk].binds(n,within_edge_set=vqe) and \
                                 theds.nodes[bk].binds(n,within_edge_set=edges_pass1) } ; 

            if len(partners_this_node) >= rescue_deg : 
                nodes_pass2.add(nk) ;
                break ; 

    elif nwd and nk in node_pass1_all and theds.nodes[nk].degree(within_edge_set=vqe) >= rescue_deg :
        nodes_pass2.add(nk) ; 
    elif nk in node_pass1_all and b4us(nk) in rescued or afterus(nk) in rescued : 
        nodes_pass2.add(nk) ; 
        nnodes_rescued  += 1 ; 

#edges_pass2 ={ e for e in edges_pass1 if {e.to.key,e.whence.key}.issubset(nodes_pass2) } ; 
edges_pass2=set() ;
for bk in baitkeys : 

    real_partners_this_node={ nk for nk in nodes_pass2 \
     if theds.nodes[bk].binds(nk,within_edge_set=edges_pass1|reinforcing_edges)}

    edges_pass2 |= { e for e in edges_pass1 | reinforcing_edges\
     if {e.to.key,e.whence.key}.issubset(real_partners_this_node)}

unitransform=lambda x : 7.0 if x==0.0 else -1 * np.log10(x) ;
ie.print_springs(edges_pass2,print_headers=True,print_weights=True,transform_scores=unitransform,\
 print_quals=True,fname=outfilename) ; 

sys.stdout.write("Nodes:\n  Pass 1: {}\n    Strong: {}\n  Pass 2: {}\n    Rescued : {}\n\n".format(\
len(node_pass1_all),len(node_pass1_strong),len(nodes_pass2),nnodes_rescued)) ; 

edgequals_1={ e.qual for e in edges_pass1 } ;
edgequals_2={ e.qual for e in edges_pass2 } ;

sys.stdout.write("Edges:\n  Pass 1: {}\n".format(len(edges_pass1))) ; 
for eq in edgequals_1 : 
    sys.stdout.write("{: <12}: {}\n".format(eq,len({ e for e in edges_pass1 if e.qual == eq }))) ; 

sys.stdout.write("\n  Pass 2: {}\n".format(len(edges_pass2))) ; 
for eq in edgequals_2 : 
    sys.stdout.write("{: <12}: {}\n".format(eq,len({ e for e in edges_pass2 if e.qual == eq }))) ; 

if idbfilename :
    theds.save(idbfilename,nodes=nodes_pass2,edges=edges_pass2) ; 
