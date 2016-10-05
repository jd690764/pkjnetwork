from django.core.management.base import BaseCommand
from django.db import connection

from network.models import Entrez

import lib.interactors as I
import lib.MSpreprocess as ms
from lib.markutils import *
from lib import config as cf

mrmspath      = cf.mrmsfilesPath
rawpath       = cf.rawfilesPath
ipath         = cf.ifilesPath
bgpath        = cf.bgerfilePath
instruction_f = open( cf.bgerfilePath )

pepDict       = { '9606': 'RPHs', '10090': 'RPMm' }

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

            dataset.syncToEntrez( bestpepdb = pepDict[ org ], debug = True )
            if bgfilename and bgfilename != '': 
                dataset.set_background( bgpath + bgfilename, bestpepdb = pepDict[ org ] ) 

            dataset.setBait(baitsym)
            dataset.score() 
            dataset.save(outfname) 


    def handle(self, *args, **options):
        self._process_datasets()

    
