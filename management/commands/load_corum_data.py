import os
import re

from django.db import connection
from django.core.management.base import BaseCommand

import pyexcel as pe

from network.models import Interaction, Entrez
from lib.fileUtils import downloadFromUrl
from lib import config as cf

import pprint

path   = 'data/interactions/'
final  = path+'corum_latest'
files  = [ 'http://mips.helmholtz-muenchen.de/genre/proj/corum/allComplexes.csv', path + 'corum.csv', path + 'corum_by_gene.tsv' ]

org    = { 'Human' : '9606', 'Mouse' : '10090' }
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
        downloadFromUrl( files[0], files[1] )
            
    def _load_dbtable( self ):

        Interaction.objects.filter( srcdb = 'CORUM' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_translate_file( self ):

        # column indexes to keep - delimiter is ';'
        # 0  - Complex id
        # 1  - Complex name
        # 2  - Synonyms
        # 3  - organism
        # 4  - subunits (UniProt IDs)
        # 5  - subunits (Entrez IDs) (separated by ,)
        # 6  - protein complex purification method (several)
        # 7  - PubMed id (single)
        # 8  - FunCat categories
        # 9  - "functional comment"
        # 9  - "disease comment"
        # 10 - "subunit comment"
        # 
        
        keep     = [0,2] 
        entrez   = { str(x['eid']): [ x['symbol'], x['swissprot']] for x in Entrez.objects.values( 'eid', 'symbol', 'swissprot' )}
        #pp.pprint( entrez )
        inp      = files[1]
        outp     = final
        by_gene  = dict()
        out_byg  = files[2]
        interids = dict()
        
        with open(outp, 'wt') as oh:
            # very little to do
            with open( inp, 'rt' ) as f:
                for line in f:

                    # skip if header
                    if re.search( '^Complex.*', line ):
                        continue
                    
                    line   = line.rstrip( )
                    fields = line.split( ";" )
                    fields[1] = re.sub( '\t', ' ', fields[1])
                    # the entrez ids may look like this:
                    #    83501,84353,(29627,29628),(84016,171571),(140591,140592)
                    # where ids within parenthesis cannot be distinguished unambiguously
                    # I take the first of the subgroup
                    while re.search( '[\(\)]', fields[5] ):
                        #print('before:' + fields[5] )
                        fields[5] = re.sub( '^(.*)\(([^,]+)[^\)]+\)(.*)$', '\\1\\2\\3', fields[5] )
                        #print('after:' + fields[5] )
                    eids   = fields[5].split( ',' )
                    #print( fields[5] )
                    # convert organism to taxid
                    m      = re.match( '.*(Mouse|Human).*', fields[3] )
                    if m:
                        fields[3] = org[ m.group(1)]
                    else:
                        print( 'non-mouse/human complex:' + fields[3] )
                        continue

                    print( fields[1] )

                    for eid in eids :
                        if eid in entrez and eid in by_gene:
                            by_gene[ entrez[eid][0] ] = by_gene[ entrez[eid][0] ] + ',' + fields[ 1 ]
                        elif eid in entrez:
                            by_gene[ entrez[eid][0] ] = fields[ 1 ]
                        else:
                            print(str(eid) + ' is not in entrez')
                            
                    for i in range( 0, len(eids)-1 ):
                        for j in range( i+1, len(eids) ):
                            if fields[1] in interids:
                                interids[ fields[1]] = interids[ fields[1]] + 1
                            else:
                                interids[ fields[1]] = 1
                                
                            index = fields[1] + '_' + str(i) + '-' + str(j) + '.' + str(fields[1]) + '.' + str( interids[ fields[1]] )

                            if eids[i] in entrez and eids[j] in entrez:
                                print( 'all: ' + str(len(eids)) + '   i: ' + str(i) + '   j: ' + str(j) + '   good' )
                                row = [ index, eids[i], eids[j], entrez[eids[i]][0], entrez[eids[j]][0], fields[3], fields[3], fields[6]  ]
                                # interid, entrezA, B, symbolA, B, taxidA, B, system, systemtype, throughput, score, pmid, source
                                oh.write( "\t".join([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], '', '', '0.0', fields[7], 'CORUM' ]) + "\n")
                            elif eids[i] == '0' or eids[j] == '0':
                                print( 'all: ' + str(len(eids)) + '   i: ' + str(i) + '   j: ' + str(j) + '   pass' )                                
                                pass
                            else:
                                print( 'all: ' + str(len(eids)) + '   i: ' + str(i) + '   j: ' + str(j) + '   obs' )
                                # these rejects are obsolete ids
                                print( 'obsolete: ',  index, "\t", eids[i], "\t", eids[j] )

        with open( out_byg, 'wt' ) as bgh:
            for k in by_gene:
                bgh.write( "\t".join([k, by_gene[k]]) + "\n" )
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
            self._export_ifile() 
