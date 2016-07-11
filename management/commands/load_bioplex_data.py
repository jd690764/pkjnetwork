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
files  = { 'http://wren.hms.harvard.edu/bioplex/data/BioPlex_interactionList_v4.tsv' : [ path+'bioplex_latest' ]}

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_bioplex( self ):

        # download file
        for url, f in files.items():
            # download file
            downloadFromUrl( url, f[0] )
            
    def _load_dbtable( self ):
        
        Interaction.objects.filter( srcdb = 'BIOPLEX' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_update_file( self ):

        # column indexes to keep
        # entrezA, B, symbolA, B, ...
        keep  = [0,1,4,5,6,7,8]
        entrez = Entrez.objects.values( 'eid', 'symbol' )
        edict  = {}
        for dic in entrez:
            edict[dic[ 'eid' ]] = dic[ 'symbol' ]        
                   
        for k, v in files.items():
            inp  = v[0]
            outp = final
            with open(outp, 'wt') as oh:
                # very little to do
                with open( inp, 'rt' ) as f:
                    counter = 1
                    for line in f:
                        
                        # skip header
                        if re.search( '^Gene', line ):
                            continue

                        line   = line.rstrip( '\n')
                        fields = line.split( "\t" )

                        # keep symbols up-to-date
                        if int(fields[0]) in edict:
                            fields[4]  = edict[ int(fields[ 0 ])]
                        if int(fields[1]) in edict:
                            fields[5]  = edict[ int(fields[ 1 ])]

                        # remove unwanted fields
                        fields = [ fields[i] for i in keep ]
                        # add an index field
                        fields.insert( 0, 'bioplex_' + str(counter) )

                        # add organismA/B fields after symbols (both 9606)
                        fields.insert( 5, '9606' )
                        fields.insert( 5, '9606' )
                        
                        oh.write( "\t".join( [fields[0], fields[1], fields[2], fields[3], fields[4],
                                              fields[5], fields[6], 'Affinity Capture-MS', 'physical', 'High', fields[9],
                                              '26186194', 'BIOPLEX' ]) + "\n")
                        counter = counter + 1
                        
        os.remove( inp )
                    
    def handle(self, *args, **options):
        self._download_from_bioplex()
        self._parse_update_file()
        self._load_dbtable()

