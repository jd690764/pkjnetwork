from django.core.management.base import BaseCommand
from lib import genehasher
from lib.fileUtils import downloadFromUrl, gunzip
import subprocess
import os
from network.models import Cdd
from django.db import connection

import pickle
from lib import genehasher as gh

import pprint
pp = pprint.PrettyPrinter(indent=4, compact=True, depth=2)

path  = 'data/protein/'
path2 = 'data/pickles/'
files = [ 'ftp://ftp.ncbi.nih.gov/pub/mmdb/cdd/family_superfamily_links',
          'ftp://ftp.ncbi.nih.gov/pub/mmdb/cdd/cddid.tbl.gz',
          path+'family_superfamily_links.txt',
          path+'cddid.tbl.gz',
          path+'cddid.txt',
          path+'cdd_latest',
          path2+'cdd_latest'
]

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_ncbi_cdd( self ):

            downloadFromUrl( files[0], files[2] )
            downloadFromUrl( files[1], files[3] )
            gunzip( files[3], path, files[4] )

    def _load_dbtable( self ):

        # load data into entrez table
        Cdd.objects.all().delete()
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.cdd FIELDS TERMINATED BY "\t" ignore 1 lines' + 
                       ' (PSSM, ACC, NAME, DESCRIPTION, ROOT, SUB, SUPER)', [ files[5] ] )

        Cdd.objects.filter( super = 0 ).update(super = None)    
            
    def _parse_file( self ):

        cdd = dict()
        with open( files[2] ) as cddTree:
            with open( files[4] ) as cddAttr:
                cdd  = gh.createCDDtree( cddTree, cddAttr, False )

        #pp.pprint(cdd['ByPssm'])        
        pickle.dump( cdd, open( files[6], 'wb' ))
        fout = open( files[5], 'wt' )
        fout.write( '\t'.join([ 'Pssm', 'Acc', 'Name', 'Desc', 'Root', 'Sub', 'Super' ]) + "\n" )
        for d in list( cdd['ByPssm'].values()) :
            sub = ''
            if type( d['Sub']) is list:
#                print( 'yes, sub is a list' )
                sub = ';'.join( [ d['Sub'][i]['Pssm'] for i in range(len(d['Sub'])) ] )

#            print(  type(d['Sub'])  )
            sup = '' #d['Root']['Pssm']
            if isinstance( d['Super'], dict ):
#                print('yes, super is a dict')
                sup = d['Super']['Pssm']

            fout.write( '\t'.join([ d['Pssm'], d['Acc'], d['Name'], d['Desc'],
                                    d['Root']['Pssm'], sub, sup ]) + "\n")
#            print( type(d['Super']) )
#            print( d['Desc'])
        fout.close()

            
    def handle(self, *args, **options):
        self._download_from_ncbi_cdd()
        self._parse_file()
        self._load_dbtable()
