import re

from django.core.management.base import BaseCommand
from lib.fileUtils import downloadFromUrl, gunzip, findURL
import datetime
from network.models import Ensembl
from django.db import connection


path  = 'data/gene/'

files = { 'hs' : [ 'ftp.ensembl.org',
                   'pub/current_gff3/homo_sapiens/',
                   'Homo_sapiens\.GRCh\d+\.\d+\.gff3\.gz',
                   path+'hs.gff3.gz',
                   path+'hs.gff3',
                   path+'hs.gff3.tsv' ],
          'mm' : [ 'ftp.ensembl.org',
                   'pub/current_gff3/mus_musculus/',
                   'Mus_musculus\.GRCm\d+\.\d+\.gff3\.gz',
                   path+'mm.gff3.gz',
                   path+'mm.gff3',
                   path+'mm.gff3.tsv' ],
          'rn' : [ 'ftp.ensembl.org',
                   'pub/current_gff3/rattus_norvegicus/',
                   'Rattus_norvegicus.Rnor_\d+\.\d+\.\d+\.gff3\.gz',
                   path+'rn.gff3.gz',
                   path+'rn.gff3',
                   path+'rn.gff3.tsv' ]
}

taxids = { 'hs' : '9606',
           'mm' : '10090',
           'rn' : '10116'
           }


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_ensembl( self ):

        
        for org, f in files.items():
            dlfile = findURL( f[0], f[1], f[2] )
            print(dlfile)
            if dlfile:
                print( dlfile )
                downloadFromUrl( dlfile, f[3] )
                gunzip( f[3], path, f[4] )
            

    def _parse_file( self ):

        for org, f in files.items():
            with open( f[5], 'wt' ) as outh:
                with open( f[4] ) as fh:
                    for line in fh:
                        if not re.match( '.*(\texon\t|\tbiological_region\t|\tCDS\t|\tchromosome\t|^#|_UTR\t|\tsupercontig\t).*', line ):
                            #print( 'line=' + line )
                            line    = line.rstrip( "\n" ).split( '\t' )
                            fields  = { k: v for k, v in [kv.split( '=' ) for kv in line[8].split( ';' )]}
                            gene_id = ''
                            if 'gene_id' in fields:
                                gene_id = fields['gene_id']
                            elif 'Parent' in fields:
                                if re.match( 'gene\:.+', fields['Parent'] ):
                                    gene_id = fields['Parent'].split(':')[1]
                            id = fields['ID'].split(':')[1]
                            outh.write( '\t'.join( [ line[0], # chrom
                                                     line[1], # authority
                                                     line[2], # gene type
                                                     line[3], # start coord
                                                     line[4], # end coord
                                                     line[6], # strand
                                                     id, # ensembl id
                                                     fields['Name'], # name
                                                     gene_id, # ensembl_id for gene
                                                     fields['biotype'], # type
                                                     taxids[org] ] # taxid
                            ) + '\n' )
                            
    def _load_dbtable( self ):

        # load data into entrez table
        Ensembl.objects.all().delete()
        for org, f in files.items():
            with connection.cursor() as c:
                c.execute( "LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.ensembl FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '\"'", [ f[5] ] )

        
    def handle(self, *args, **options):
        print( '\n\n\n\n############################ ' + 'update Ensembl data on ' + str(datetime.date.today()))
        self._download_from_ensembl()
        self._parse_file()
        self._load_dbtable()
