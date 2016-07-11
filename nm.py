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
# interactors_extras mostly contains useful bells and whistles

import logging
logger = logging.getLogger('django')

import pprint
pp = pprint.PrettyPrinter(indent=4)

def createNetwork( request ):
    files     = os.listdir('data/nwfiles/')
    yamlfiles = filter(lambda x:re.search(r'.*yaml$', x), files)
    return render( request, 'network/createNetwork.html', { yamlfiles : yamlfiles } )

def display( request ):

    
    choices = {}#     choices = request.POST
    with open('tmp/random_edges_out.cyt') as f:
        counter = 1
        for line in f:
            choices[ counter ] = line
            counter = counter + 1
            if counter > 11:
                break
    
    return render( request, 'network/display.html', { 'choices' : choices } )

