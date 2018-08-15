import os
import re
import datetime

from django.db import connection
from django.core.management.base import BaseCommand

from network.models import Interaction, Entrez
from lib.fileUtils import unzip, downloadFromUrl

path = 'data/interactions/'
final = path+'biogrid_data_latest'
files  = { 'https://downloads.thebiogrid.org/Download/BioGRID/Latest-Release/BIOGRID-ALL-LATEST.tab2.zip' : [ path+'biogrid.zip', path+'biogrid_latest' ]}

src_by_pmids = {'26186194': 'BIOPLEX', '28514442': 'BIOPLEXv2', '22939629': 'EMILI', '26344197': 'EMILIv2', '23193263': 'PREPPI', '23023127': 'PREPPI' } # skip these datasets - they are loaded separately

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--reload',
            action  = 'store_true',
            dest    = 'reload',
            default = False,
            help    = 'Reload table and do nothing else',
        )
        parser.add_argument(
            '--reparse',
            action  = 'store_true',
            dest    = 'reparse',
            default = False,
            help    = 'Reparse previously downloaded data and reload table',
        )
        

    def _download_from_biogrid( self ):

        # download file
        if os.path.exists( final ):
            os.rename( final, final+'_old' )

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
        
        Interaction.objects.filter( srcdb__in = 'BIOGRID').delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_update_file( self ):

        # column indexes to keep
        # (interid, entrezA, B, symbolA, B, system, systemtype, pmid, taxidA, B, throughput, score, source
        keep   = [0,1,2,7,8,11,12,14,15,16,17,18,23] 
        entrez = Entrez.objects.values( 'eid', 'symbol' )
        edict  = {}
        #print( len(entrez))
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
                        if fields[14] in src_by_pmids:
                            # avoid duplications
                            #fields[23] = src_by_pmids[ fields[14] ]
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
            
        #os.remove( inp )

        
    def handle(self, *args, **options):
        print( '\n\n\n\n############################ ' + 'update Biogrid data on ' + str(datetime.date.today()))
        if options[ 'reload' ]:
            self._load_dbtable()
        elif options[ 'reparse' ]:
            self._parse_update_file()
            self._load_dbtable()
        else:
            self._download_from_biogrid()
            self._parse_update_file()
            self._load_dbtable()
