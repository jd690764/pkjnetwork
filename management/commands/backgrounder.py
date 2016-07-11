from django.core.management.base import BaseCommand
from django.db import connection

from network.models import Entrez

import lib.interactors as I
import lib.MSpreprocess as ms
from lib.markutils import *


mrmspath = '/srv/msrepo/mrmsfiles/'
rawpath  = '/srv/msrepo/rawfiles/'
ipath    = '/srv/msrepo/ifiles/' #'data/preprocess/' #
bgpath   = '/srv/msrepo/background/'
instruction_f = open( 'data/preprocess/backgrounder.tsv' )

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _process_datasets( self ):
        for line in instruction_f : 
            if line[0] == '#' : 
                continue 

            linel       =    line[:-1].split('\t') 
            rawfilename =    linel[0]
            infilename  =    linel[1] 
            baitsym     =    b4us(linel[2]) 
            org         =    linel[3]
            special     =    linel[4]
            parser      =    linel[5] 
            print( linel[5] )
            bgfilename  =    linel[6] 
            print('infile=' + infilename)
            if special and special[0] == '*' : 
                outfname_pfx   =    special[1:]+date6()
            elif special : 
                outfname_pfx   =    baitsym+'_'+org+'_'+special+'_'+date6() 
            else : 
                outfname_pfx   =    baitsym+'_'+org+'_'+date6() 

            outfname = ipath + outfname_pfx + '.i'

            sys.stdout.write(outfname+'\n') 

            if 'mrms' in infilename : 
                infile = open( mrmspath + infilename ) 
            elif 'xml' in infilename : 
                infile = open( rawpath + infilename, 'rb' ) 
            else : 
                raise TypeError  

            dataset = ms.MSdata( outfname_pfx )

            if parser == 'SUMS' :
                dataset.parseSUMS(infile) 
            elif parser == 'Lane' :
                dataset.parseLane(infile) 
            elif parser == 'XML'  :
                dataset.parseXML(infile) 
            else : 
                raise TypeError 

            if org == '9606' : 
                dataset.syncToEntrez() 
            else : 
                dataset.syncToEntrez( bestpepdb = 'RPMm', debug = True ) 

            if bgfilename : 
                dataset.set_background( bgpath + bgfilename ) 

            dataset.setBait(baitsym) 
            dataset.score() 
            dataset.save(outfname) 


    def handle(self, *args, **options):
        self._process_datasets()

    
