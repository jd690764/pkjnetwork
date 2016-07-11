from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

import sys
from numpy import log, exp
from lib import interactors as I
# interactors handles the main 'node', 'edge','interaction', and 'dataSet' classes
from lib import interactors_extras as ie
from os import listdir
import re
from lib import networkMaker as nm

# interactors_extras mostly contains useful bells and whistles

import logging
logger = logging.getLogger('django')

import pprint
pp = pprint.PrettyPrinter(indent=4)

def createNetwork( request ):
    files     = listdir('data/nwfiles/')
    yamlfiles = dict()
    for f in files:
        if re.search( '.*yaml$', f ):
            yamlfiles[f] = f

    for k in yamlfiles:
        print( k + ' ' + yamlfiles[k] )
    return render( request, 'network/createNetwork.html',  { 'yamlfiles' : yamlfiles } )

def display( request ):

    fname = request.POST['yaml']
    print( 'fname=' + fname )
    nm.createNetwork( 'data/nwfiles/' + fname )
    
    choices = {}#     choices = request.POST
    with open('tmp/gleeson_medium.cyt') as f:
        counter = 1
        for line in f:
            choices[ counter ] = line
            counter = counter + 1
            if counter > 11:
                break
    
    return render( request, 'network/display.html', { 'choices' : choices } )

