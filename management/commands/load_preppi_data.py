import os
import re

from django.core.management.base import BaseCommand
from django.db import connection

from network.models import Interaction, Entrez

path = 'data/interactions/'
source = path+'preppi_150727_lr600.i' #static file
final = path+'preppi_updated'
class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'
            
    def _load_dbtable( self ):
        
        Interaction.objects.filter(srcdb = 'PREPPI').delete()

        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t" ignore 1 lines', [final] )
        
    def _update_file( self ):
        entrez = Entrez.objects.values( 'eid', 'symbol' )
        edict  = {}
        for dic in entrez:
            edict[dic[ 'eid' ]] = dic[ 'symbol' ]

        with open(final, 'wt') as oh:
            with open( source, 'rt' ) as f:
                for line in f:

                    line   = line.rstrip( '\n')
                    fields = line.split( "\t" )

                    if re.search( '^ID', line ):
                        oh.write( line + "\n" )
                        continue
                               
                    
                    if int(fields[6]) not in edict or int(fields[7]) not in edict:
                        continue

                    # keep symbols up-to-date
                    fields[1]  = edict[ int(fields[ 6 ])]
                    fields[2]  = edict[ int(fields[ 7 ])]

                    oh.write( "\t".join([ fields[0], fields[6], fields[7], fields[1], fields[2], fields[4], fields[5],
                                          'computational', 'physical', '', fields[3], '23193263', 'PREPPI' ]) + "\n" )
            
    def handle(self, *args, **options):
        self._update_file()
        self._load_dbtable()
