import os
import re

from django.db import connection
from django.core.management.base import BaseCommand

from network.models import Interaction, Entrez
from lib.fileUtils import downloadFromUrl
from lib import config as cf

import pprint

path   = 'data/interactions/'
final  = path+'intact_complex_latest'
files  = [ 'ftp://ftp.ebi.ac.uk/pub/databases/intact/complex/current/complextab/homo_sapiens.tsv', 'ftp://ftp.ebi.ac.uk/pub/databases/intact/complex/current/complextab/mus_musculus.tsv', path + 'intact_complex.csv' ]

org    = { 'Human' : '9606', 'Mouse' : '10090' }
rescue = { 'A0A0N4SUT9' : [ 'Brpf1', 78783 ], 'A2ACT7' : [ 'Col9a3', 12841 ], 'A2AGL3' : [ 'Ryr3', 20192 ], 'B1AVK5' : [ 'Col4a6', 94216 ], 'B2KF05' : [ 'Brpf3', 268936 ], 'B2RQR7' : [ 'Col25a1', 77018 ], 'B2RUS7' : [ 'Abcc8', 20927 ], 'B2RX82' : [ 'Chrna10', 504186 ], 'E9PWW9' : [ 'Rsf1', 233532 ], 'E9PZ26' : [ 'Brd1', 223770 ], 'E9Q2Z1' : [ 'Cecr2', 330409 ], 'E9Q7P1' : [ 'Col22a1', 69700 ], 'G3X8Z7' : [ 'Chrna9', 231252 ], 'Q0VBD0' : [ 'Itgb8', 320910 ], 'Q3V3N7' : [ 'Bbs1', 52028 ], 'Q63ZW6' : [ 'Col4a5', 12830 ], 'Q91VA7' : [ 'Idh3b', 170718 ], 'Q9BXH1' : [ 'BBC3', 27113 ], 'Q9JLI2' : [ 'Col5a3', 53867 ], 'Q9WVA7' : [ 'Peg12', 27412 ], 'A2A654' : [ 'Bptf', 207165 ], 'A2ASS6' : [ 'Ttn', 22138 ], 'E9PWQ3' : [ 'Col6a3', 12835 ], 'O08742' : [ 'Gp5', 14729 ], 'O70507' : [ 'Hcn4', 330953 ], 'O88379' : [ 'Baz1a', 217578 ], 'O88874' : [ 'Ccnk', 12454 ], 'P01942' : [ 'Hba', 15121 ], 'P02468' : [ 'Lamc1', 226519 ], 'P04760' : [ 'Chrng', 11449 ], 'P05555' : [ 'Itgam', 16409 ], 'P22777' : [ 'Serpine1', 18787 ], 'P23198' : [ 'Cbx3', 12417 ], 'P24063' : [ 'Itgal', 16408 ], 'P28574' : [ 'Max', 17187 ], 'P35441' : [ 'Thbs1', 21825 ], 'P49718' : [ 'Mcm5', 17218 ], 'P50538' : [ 'Mxd1', 17119 ], 'P53657' : [ 'Pklr', 18770 ], 'P54099' : [ 'Polg', 18975 ], 'P61622' : [ 'Itga11', 319480 ], 'Q02789' : [ 'Cacna1s', 12292 ], 'Q07643' : [ 'Col9a2', 12840 ], 'Q14BL5' : [ 'Itga10', 213119 ], 'Q3V0T4' : [ 'Itgad', 381924 ], 'Q60680' : [ 'Chuk', 12675 ], 'Q61092' : [ 'Lamc2', 16782 ], 'Q61315' : [ 'Apc', 11789 ], 'Q61738' : [ 'Itga7', 16404 ], 'Q64436' : [ 'Atp4a', 11944 ], 'Q6PGF3' : [ 'Med16', 216154 ], 'Q80YP0' : [ 'Cdk3-ps', 69681 ], 'Q810T2' : [ 'Ccnb3', 209091 ], 'Q8BZ21' : [ 'Kat6a', 244349 ], 'Q8R418' : [ 'Dicer1', 192119 ], 'Q91YD5' : [ 'Itga9', 104099 ], 'Q91YE5' : [ 'Baz2a', 116848 ], 'Q924H2' : [ 'Med15', 94112 ], 'Q9D855' : [ 'Uqcrb', 67530 ], 'Q9D8B4' : [ 'Ndufa11', 69875 ], 'Q9ESY2' : [ 'Pfkfb3', 170768 ], 'Q9QXG9' : [ 'Tinf2', 28113 ], 'Q9R117' : [ 'Tyk2', 54721 ], 'Q9WUJ8' : [ 'Orc6', 56452 ], 'Q9Z1K7' : [ 'Apc2', 23805 ]}
pp     = pprint.PrettyPrinter( indent = 4 )

class Command(BaseCommand):
#    args = '<foo bar ...>'
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
    
    def _download_from_database( self ):
        downloadFromUrl( files[0], files[2] )
        downloadFromUrl( files[1], files[2], True )
            
    def _load_dbtable( self ):

        Interaction.objects.filter( srcdb = 'INTCOMP' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_translate_file( self ):

        # column indexes to keep - delimiter is tab
        # 0 - Complex ac
        # 1 - Recommended name
        # 2 - Aliases for complex
        # 3 - Taxonomy identifier
        # 4 - Identifiers (and stoichiometry) of molecules in complex (sp ids)
        # 5 - Confidence
        # 6 - Experimental evidence
        # 7 - Go Annotations
        # 8 - Cross references (includes pmids), e.g.: 'pubmed:1916105(see-also)|pubmed:17876790(see-also)|matrixdb:MULT_53_human(identity)'
        # 9 - Description
        # 10- Complex properties
        # 11- Complex assembly
        # 12- Ligand
        # 13- Disease
        # 14- Agonist
        # 15- Antagonist
        # 16- Comment
        # 17- Source
        # 
        
        keep     = [0,1,3,4,8,11] 
        entrez   = { str(x['swissprot']): [ x['symbol'], x['eid']] for x in Entrez.objects.values( 'eid', 'symbol', 'swissprot' )}
        #pp.pprint( entrez )
        inp      = files[2]
        outp     = final
        #by_gene  = dict()
        #out_byg  = files[2]
        #interids = dict()
        
        with open(outp, 'wt') as oh:
            # very little to do
            with open( inp, 'rt' ) as f:
                for line in f:

                    # skip if header
                    if re.search( '^#Complex', line ):
                        continue
                    
                    line      = line.rstrip( )
                    fields    = line.split( "\t" )

                    # get pubmed ids from fields[8]
                    fields[8] = '|'.join(re.findall('pubmed\:(\d+)', fields[8]))
                    #print( fields[8] )

                    # skip homooligomers
                    if re.search( r'^homo', fields[11] ):
                        continue

                    # the swissprot ids may look like this:
                    #     P49642(1)|P09884(1)|Q14181(1)|P49643(1)   
                    # numbers in parentheses: stoichiometry
                    # 
                    #print('before:' + fields[4] )
                    fields[4] = re.sub( '\(\d+\)', '', fields[4] )
                    #print('after:' + fields[4] )
                    
                    spids     = fields[4].split( '|' )
                    symbols   = list()
                    eids      = list()
                    for spid in spids:
                        spid = re.sub( r'^(.+)-.+$', r'\1', spid )
                        if spid in entrez:
                            symbols.append( entrez[ spid ][0] )
                            eids.append( entrez[ spid ][1] )
                        elif spid in rescue:
                            symbols.append( rescue[ spid ][0] )
                            eids.append( rescue[ spid ][1] )                            
                        else:
                            print( spid + ' is not in entrez' )
                    
                    for i in range( 0, len(symbols)-1 ):
                        for j in range( i+1, len(symbols) ):

                            index = fields[1] + '.' + str(fields[0]) + '.' + str(fields[3]) + '_' + str(i) + '-' + str(j) 

                            #print( 'all: ' + str(len(eids)) + '   i: ' + str(i) + '   j: ' + str(j) + '   good' )
                            # interid, entrezA, B, symbolA, B, taxidA, B, system, systemtype, throughput, score, pmid, source
                            oh.write( "\t".join([index, str(eids[i]), str(eids[j]), symbols[i], symbols[j], str(fields[3]), str(fields[3]), '', '', '', '0.0', fields[8], 'INTCOMP' ]) + "\n")

        #os.remove( inp )

    def _export_ifile( self ):

        corum = Interaction.objects.filter( srcdb = 'CORUM' ).values( 'interid', 'entreza', 'entrezb', 'symbola', 'symbolb' )
        with open( cf.corumPath, 'wt' ) as outp:
        #with open( 'tets.txt', 'wt' ) as outp:
            outp.write( '\t'.join([ 'id', 'ea', 'eb', 'oa', 'ob' ]) + '\n' )
            for dic in corum:
                outp.write( '\t'.join( [ str(dic['interid']), str(dic['entreza']), str(dic['entrezb']), dic['symbola'], dic['symbolb']] ) + "\n")
        
    def handle(self, *args, **options):
        if options[ 'reload' ]:
            print('reload')
            self._load_dbtable()
        elif options[ 'reparse' ]:
            self._parse_translate_file()
            self._load_dbtable()
        else:
            print('redo')
            self._download_from_database()
            self._parse_translate_file()
            self._load_dbtable()
            #self._export_ifile() 
