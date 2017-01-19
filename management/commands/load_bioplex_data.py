import os
import re

from django.core.management.base import BaseCommand
from django.db import connection

from network.models import Interaction, Entrez
from lib.fileUtils import downloadFromUrl

path = 'data/interactions/'
final = path+'bioplex_data_latest'
if os.path.exists( final ):
    os.rename( final, final+'_old' )
files  = [ {'http://wren.hms.harvard.edu/bioplex/data/BioPlex_interactionList_v4.tsv' : [ path + 'bioplex_latest', False, 'latest' ]},
           {'http://wren.hms.harvard.edu/bioplex/data/interactome_update_Dec2015.tsv' : [ path + 'bioplex_update', False, 'update' ]},
           {'http://wren.hms.harvard.edu/bioplex/data/interactome_update_May2016.tsv' : [ path + 'bioplex_update', True, 'update' ]},
           {'http://wren.hms.harvard.edu/bioplex/data/interactome_update_Aug2016.tsv' : [ path + 'bioplex_update', True, 'update' ]},
           {'http://wren.hms.harvard.edu/bioplex/data/interactome_update_Dec2016.tsv' : [ path + 'bioplex_update', True, 'update' ]} ]

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_bioplex( self ):

        # download file
        for x in files:
            for url, f in x.items():
                # download file
                downloadFromUrl( url, f[0], f[1] )
            
    def _load_dbtable( self ):
        
        Interaction.objects.filter( srcdb = 'BIOPLEX' ).delete()
        Interaction.objects.filter( srcdb = 'BIOPLEXfp' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_update_file( self ):

        # column indexes to keep
        # entrezA, B, symbolA, B, ...
        keepLa  = [ 0,1,4,5,6,7,8 ]
        keepUp  = [ 6,4,5,3,7,8,9 ]
        entrez  = Entrez.objects.values( 'eid', 'symbol' )
        edict   = {}
        for dic in entrez:
            edict[dic[ 'eid' ]] = dic[ 'symbol' ]        

        count   = 1
        counter = 1
        for x in files:
            for k, v in x.items():
                inp    = v[0]
                outp   = final
                keep   = keepLa if v[2] == 'latest' else keepUp
                srcdb  = 'BIOPLEX' if v[2] == 'latest' else 'BIOPLEXfp'
                append = 'wt' if v[2] == 'latest' else 'at'
                if count > 2:
                    continue
                count  = count + 1
                print( inp + ' ' + srcdb + ' ' + append )            
                with open(outp, append) as oh:
                    # very little to do
                    with open( inp, 'rt' ) as f:
                        for line in f:

                            # skip header
                            if re.search( '^(Gene|plate_num)', line ):
                                continue

                            line   = line.rstrip( '\n')
                            fields = line.split( "\t" )
                            #print( '-'.join(fields) + '\n')
                            # remove unwanted fields
                            fields = [ fields[i] for i in keep ]
                            #print( '+'.join(fields) + '\n')
                            if fields[0] == '' or fields[1] == '':
                                continue

                            # keep symbols up-to-date
                            if int(fields[0]) in edict:
                                fields[2]  = edict[ int(fields[ 0 ])]
                            if int(fields[1]) in edict:
                                fields[3]  = edict[ int(fields[ 1 ])]

                            # add an index field
                            fields.insert( 0, 'bioplex_' + str(counter) )

                            # add organismA/B fields after symbols (both 9606)
                            fields.insert( 5, '9606' )
                            fields.insert( 5, '9606' )

                            oh.write( "\t".join( [fields[0], fields[1], fields[2], fields[3], fields[4],
                                                  fields[5], fields[6], 'Affinity Capture-MS', 'physical', 'High', fields[9],
                                                  '26186194', srcdb ]) + "\n")
                            counter = counter + 1
                        
        os.remove( inp )
                    
    def handle(self, *args, **options):
        self._download_from_bioplex()
        self._parse_update_file()
        self._load_dbtable()

