import os
import re

from django.db import connection
from django.core.management.base import BaseCommand

import pyexcel as pe

from network.models import Interaction, Entrez
from lib.fileUtils import unzip, downloadFromUrl

import pprint

path   = 'data/interactions/'
final  = path+'emiliome_data_latest'
files  = { 'http://human.med.utoronto.ca/download/TableS3.xls' : [ path+'emiliome.xlsx', path+'emiliome.tsv', path+'emiliome_processed' ]}

# for a few genes, entrez has alternative spids
corr   = { 'P62861' : 'P35544',
           'Q5SNT6' : 'Q641Q2',
           'Q96PK2' : 'Q9UPN3',
}

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_labsite( self ):
        ###################
        # did this manually - could not open xls file
        # download file
        for url, f in files.items():
            # download file
            downloadFromUrl( url, f[0] )

            # extract appropriate sheet
            book = pe.get_book(file_name=f[0])
            book['Predicted_complexes'].save_as( f[1] )

            os.remove( f[0] )
            
    def _load_dbtable( self ):

        Interaction.objects.filter( srcdb = 'EMILI' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_translate_file( self ):

        # column indexes to keep
        # only the name of complex and list of ids
        keep     = [0,2] 
        entrez   = Entrez.objects.values( 'eid', 'symbol', 'swissprot' )
        pepdict  = {}
        for dic in entrez:
            dic['swissprot'] = re.sub( r'\.\d+$', '', dic['swissprot'])
            pepdict[ dic['swissprot'] ] = [ dic['symbol'], dic['eid'] ]

        for k, v in files.items():
            inp  = v[1]
            outp = final
            with open(outp, 'wt') as oh:
                # very little to do
                with open( inp, 'rt' ) as f:
                    for line in f:

                        # skip if header
                        if not re.search( '^C_', line ):
                            continue

                        line   = line.rstrip( '\n')
                        fields = line.split( "\t" )
                        spids  = fields[2].split( ',' )

                        for i in range( 0, len(spids)-1 ):
                            for j in range( i+1, len(spids) ):
                                index = fields[0] + '_' + str(i) + '_' + str(j)

                                # correct a few mismapped spids
                                if spids[i] in corr:
                                    spids[i] = corr[ spids[i] ]
                                elif spids[j] in corr:
                                    spids[j] = corr[ spids[j] ]
                                    
                                if spids[i] in pepdict and spids[j] in pepdict:
                                    row = [ index, str(pepdict[spids[i]][1]), str(pepdict[spids[j]][1]), pepdict[spids[i]][0], pepdict[spids[j]][0], '9606', '9606'  ]
                                    oh.write( "\t".join([row[0], row[1], row[2], row[3], row[4], row[5],
                                                         row[6], 'Co-purification', 'physical', '', '', '22939629', 'EMILI' ]) + "\n")
                                else:
                                    # these rejects are obsolete ids
                                    print( index, "\t", spids[i], "\t", spids[j] )
        #os.remove( inp )

        
    def handle(self, *args, **options):
        #self._download_from_labsite()
        self._parse_translate_file()
        self._load_dbtable()
