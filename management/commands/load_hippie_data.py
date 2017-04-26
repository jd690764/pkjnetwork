import os
import re
import datetime

from django.db import connection
from django.core.management.base import BaseCommand

from network.models import Interaction, Entrez
from lib.fileUtils import unzip, downloadFromUrl
import pprint
from lib import config as cf 

path     = 'data/interactions/'
final    = path+'hippie_data_latest'
files    = [ 'http://cbdm-01.zdv.uni-mainz.de/~mschaefer/hippie/hippie_current.txt', path+'hippie_current.txt']
ifile    = cf.hippiePath

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
        

    def _download_data( self ):

        # download file
        if os.path.exists( final ):
            os.rename( final, final+'_old' )

        # download file
        downloadFromUrl( files[0], files[1] )

            
    def _load_dbtable( self ):
        
        Interaction.objects.filter( srcdb = 'HIPPIE' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t" ' +
                       '(INTERID, ENTREZA, ENTREZB, SYMBOLA, SYMBOLB, ORGANISMA, ORGANISMB, SYSTEM, SYSTEMTYPE, THROUGHPUT, SCORE, SRCDB, pmid)', [final] )

            
    def _parse_update_file( self ):

        # column indexes to keep
        # sp_acca, entreza, sp_accb, entrezb, confidence, info
        # the info column has this structure:
        #     experiments:a,b,...;pmids:1,2,3...;sources:a,b,...

        counter = 1
        edict   = { x['eid'] : x['symbol'] for x in Entrez.objects.values( 'eid', 'symbol' )}
        with open( final, 'wt' ) as oh:
            with open( files[1], 'rt' ) as ih:
                for line in ih:
                    line   = line.rstrip( )
                    fields = line.split( "\t" )
                    fields[1] = int( fields[1] )
                    fields[3] = int( fields[3] )
                    
                    if fields[1] not in edict or fields[3] not in edict:
                        print( 'problem with ' + str(fields[1]) + ' or ' + str(fields[3]) )
                        counter = counter + 1
                        continue # skip if entrezid is not recognized
                    if len(fields) < 6:
                        print( '+'.join(map(str, fields)))
                        fields.append( '' )
                    m      = re.match( r'^experiments\:([^;]+);?.*', fields[5] ) 
                    if m is not None:
                        expts = m.group(1)
                        expts = re.sub( r',', r'|', expts )
                    m      = re.match( r'.*pmids\:([^;]+);?.*', fields[5] ) 
                    if m is not None:
                        pmids = m.group(1)
                        pmids = re.sub( r',', r'|', pmids )
                    m      = re.match( r'.*sources\:(.+)$', fields[5] ) 
                    if m is not None:
                        srcs  = m.group(1)
                        srcs  = re.sub( r',', r'|', srcs )

                    oh.write( '\t'.join([ 'hippie'+str(counter), str(fields[1]), str(fields[3]), edict[ fields[1] ], edict[ fields[3] ],
                                          '9606', '9606', expts, '', srcs, fields[4], 'HIPPIE', str(pmids) ]) + '\n' )
                    counter   = counter + 1
        #os.remove( inp )

    def _export_ifile( self ):

        with open(ifile, 'wt') as oh:
            oh.write( '\t'.join([ 'interID', 'entrezA', 'entrezB', 'biogridA', 'biogridB', 'systematicA', 'systematicB', 'officialA', 'officialB', 'synonymsA', 'synonymsB', "system" , "systemType" , "Author" , "pmid" , 'organismA', 'organismB', "throughput" , "score" , "modification" , "phenotypes", "qualifications" , "tags" , "srcDB" ]) + '\n' )
            with connection.cursor() as c:
            # very long query, be patient ... (6-7 minutes)
                c.execute( 'select interid, entreza, entrezb, symbola, symbolb, organisma, score from interaction where srcdb = "HIPPIE"' )
                for row in c.fetchall():
                    oh.write('\t'.join( [row[0], str(row[1]), str(row[2]), '', '', '', '', row[3], row[4], '', '', '', '', '', '', str(row[5]), str(row[5]), '', str(row[6]), '', '',  '', '', 'HIPPIE' ]) + '\n')

        
    def handle(self, *args, **options):
        print( '\n\n\n\n############################ ' + 'update hippie data on ' + str(datetime.date.today()))
        if options[ 'reload' ]:
            self._load_dbtable()
            self._export_ifile()
        elif options[ 'reparse' ]:
            self._parse_update_file()
            self._load_dbtable()
            self._export_ifile()            
        else:
            self._download_data()
            self._parse_update_file()
            self._load_dbtable()
            self._export_ifile()
