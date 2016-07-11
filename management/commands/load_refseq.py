from django.core.management.base import BaseCommand
from lib.fileUtils import downloadFromUrl, gunzip
from network.models import Refseq
from django.db import connection
import subprocess
import os
import re

path  = 'data/gene/'

files = [ 'ftp://ftp.ncbi.nih.gov/gene/DATA/gene2refseq.gz',
          path + 'gene2refseq.gz', 
          path + 'refseq_latest',
          path + 'refseq_latest_final' ]

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_ncbi( self ):
        downloadFromUrl( files[0], files[1] )
        gunzip( files[1], path, files[2] )
        os.remove( files[1] )
        os.system( "grep -P '^(9606|10090)\t' " + files[2] + ' > ' + path + 'x' )
        os.rename( path + 'x', files[2] )
        
    def _load_dbtable( self ):

        # load data into refseq table
        Refseq.objects.all().delete()
        with connection.cursor() as c:
            c.execute( "LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.refseq FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '\"' ignore 1 lines " + 
                       '(taxid, eid, @status, @rnaa, @rnav, @rnagi, @pacc, @protv, @pgi, @gacc, @genv, @ggi, @scoord, @ecoord, @strand, @assembly, @pepa, @pepgi, @symb) ' +
                       'SET status = case when @status = "NA" then NULL else @status end, ' +
                       'rna_acc = case when @rnaa = "-" then NULL else @rnaa end, ' +
                       'rna_version = case when @rnav = "-" then NULL else @rnav end, ' +
                       'rna_gi = case when @rnagi = "-" then NULL else @rnagi end, ' +
                       'prot_acc = case when @pacc = "-" then NULL else @pacc end, ' +
                       'prot_version = case when @protv = "-" then NULL else @protv end, ' +
                       'prot_gi = case when @pgi = "-" then NULL else @pgi end, ' +
                       'gennuc_acc = case when @gacc = "-" then NULL else @gacc end, ' +
                       'gen_version = case when @genv = "-" then NULL else @genv end, ' +
                       'gennuc_gi = case when @ggi = "-" then NULL else @ggi end, ' +
                       'scoord = case when @scoord = "-" then NULL else @scoord end, ' +
                       'ecoord = case when @ecoord = "-" then NULL else @ecoord end, ' +
                       'strand = case when @strand = "?" then NULL else @strand end, ' + 
                       'assembly = case when @assembly = "-" then NULL else @assembly end, ' + 
                       'pept_acc = case when @pepa = "-" then NULL else @pepa end, ' +
                       'pept_gi = case when @pepgi = "-" then NULL else @pepgi end, ' +
                       'symbol = case when @symb = "-" then NULL else @symb end;', [ files[3] ])

            
    def _parse_file( self ):
        with open(files[3], 'wt' ) as outf:
            with open( files[2], 'rt' ) as inf:
                for line in inf:
                    line = line.rstrip()
                    fields = line.split( '\t' )
                    if fields[3] == '-':
                        (racc, rver) = ('-', '-')
                    else:
                        (racc, rver) = fields[3].split('.')
                    if fields[5] == '-':
                        (pacc, pver) = ('-', '-')
                    else:
                        (pacc, pver) = fields[5].split('.')
                    if fields[7] == '-':
                        (nacc, nver) = ('-', '-')
                    else:
                        (nacc, nver) = fields[7].split('.')
                    
                    outf.write( '\t'.join( [fields[0], fields[1], fields[2], racc, rver, fields[4], pacc, pver, fields[6],
                                            nacc, nver, fields[8], fields[9], fields[10], fields[11], fields[12], fields[13],
                                            fields[14], fields[15] ]) + "\n")

                    
    def handle(self, *args, **options):
        self._download_from_ncbi()
        self._parse_file( )
        self._load_dbtable()
