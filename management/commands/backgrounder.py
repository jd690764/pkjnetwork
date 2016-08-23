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

            linel           = line.rstrip().lstrip().split('\t')
            print( 'line=' + str(linel) )

            infilename      = linel[0] 
            baitsym         = b4us(linel[1]) 
            org             = linel[2]
            special         = linel[3]
            parser          = linel[4] 

            if len(linel) == 6:
                bgfilename  = linel[5]
            else :
                bgfilename  = ''

            print( 'infile=' + infilename )
            print( 'baitsym=' + baitsym )
            print( 'org=' + org )
            print( 'special=' + special )
            print( 'bgfile=' + bgfilename )

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
                if bgfilename and bgfilename != '': 
                    dataset.set_background( bgpath + bgfilename ) 

            else : 
                dataset.syncToEntrez( bestpepdb = 'RPMm', debug = True )
                if bgfilename and bgfilename != '': 
                    dataset.set_background( bgpath + bgfilename, bestpepdb = 'RPMm' ) 

            dataset.setBait(baitsym) 
            dataset.score() 
            dataset.save(outfname) 

        ms.save_dup()

    def handle(self, *args, **options):
        self._process_datasets()

    
