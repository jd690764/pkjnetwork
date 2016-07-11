import os
import re

from django.db import connection
from django.core.management.base import BaseCommand

from network.models import Interaction, Entrez
from lib.fileUtils import unzip, downloadFromUrl

path = 'data/interactions/'
final = path+'biogrid_data_latest'
if os.path.exists( final ):
    os.rename( final, final+'_old' )
files  = { 'http://thebiogrid.org/downloads/archives/Latest%20Release/BIOGRID-ALL-LATEST.tab2.zip' : [ path+'biogrid.zip', path+'biogrid_latest' ]}

skip_pmids = ['26186194', '22939629'] # skip bioplex and emili data 

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_biogrid( self ):

        # download file
        for url, f in files.items():
            # download file
            downloadFromUrl( url, f[0] )
            # unzip
            unzip( f[0], path )
            os.remove( f[0] )
            # rename
            fs = os.listdir( path )
            for fnew in fs:
                if re.search( 'BIOGRID-ALL', fnew ):
                    os.rename( path+fnew, f[1] )
            
    def _load_dbtable( self ):
        
        Interaction.objects.filter( srcdb = 'BIOGRID' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_update_file( self ):

        # column indexes to keep
        # (interid, entrezA, B, symbolA, B, system, systemtype, pmid, taxidA, B, throughput, score, source
        keep   = [0,1,2,7,8,11,12,14,15,16,17,18,23] 
        entrez = Entrez.objects.values( 'eid', 'symbol' )
        edict  = {}
        for dic in entrez:
            edict[dic[ 'eid' ]] = dic[ 'symbol' ]

        for k, v in files.items():
            inp  = v[1]
            outp = final
            with open(outp, 'wt') as oh:
                # very little to do
                with open( inp, 'rt' ) as f:
                    for line in f:

                        # skip if header
                        if re.search( '^#', line ):
                            continue

                        line   = line.rstrip( '\n')
                        fields = line.split( "\t" )

                        # what are these?
                        if fields[1] == '-' or fields[2] == '-':
                            continue
                        if fields[7] in skip_pmids:
                            continue
                        # ids are incorrect
                        if int(fields[1]) not in edict or int(fields[2]) not in edict :
                            continue

                        fields[17] = re.sub( r'\ Throughput', '', fields[17] ) # High/Low Throughput

                        # keep symbols up-to-date
                        fields[7]  = edict[ int(fields[ 1 ])]
                        fields[8]  = edict[ int(fields[ 2 ])]

                        # remove unwanted fields
                        fields = [ fields[i] for i in keep ]

                        # the order is:
                        # interid, entrezA, B, symbolA, B, taxidA, B, system, systemtype, throughput, score, pmid, source
                        oh.write( "\t".join([fields[0], fields[1], fields[2], fields[3], fields[4], fields[8],
                                             fields[9], fields[5], fields[6], fields[10], fields[11], fields[7], fields[12]]) + "\n")
            
        os.remove( inp )

        
    def handle(self, *args, **options):
        self._download_from_biogrid()
        self._parse_update_file()
        self._load_dbtable()
