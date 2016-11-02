import os
import re

from django.db import connection
from django.core.management.base import BaseCommand

from network.models import Interaction, Entrez, Hgnc
from lib.fileUtils import downloadFromUrl, gunzip
from lib import config as cf

import pprint

path          = 'data/interactions/'
final         = path+'go_complex_latest'
files         = [ 'http://geneontology.org/gene-associations/goa_human.gaf.gz', 'http://geneontology.org/gene-associations/gene_association.mgi.gz', path+'gaf.gz', path+'go_complex.csv', 'http://golr.geneontology.org/select?defType=edismax&qt=standard&indent=on&wt=csv&rows=100000&start=0&fl=annotation_class,annotation_class_label&facet=true&facet.mincount=1&facet.sort=count&json.nl=arrarr&facet.limit=25&hl=true&hl.simple.pre=%3Cem%20class=%22hilite%22%3E&csv.encapsulator=&csv.separator=%09&csv.header=false&csv.mv.separator=%7C&fq=document_category:%22ontology_class%22&fq=idspace:%22GO%22&fq=is_obsolete:%22false%22&fq=source:%22cellular_component%22&facet.field=source&facet.field=idspace&facet.field=subset&facet.field=is_obsolete&q=*complex&qf=annotation_class%5E3&qf=annotation_class_label_searchable%5E5.5&qf=description_searchable%5E1&qf=synonym_searchable%5E1&qf=alternate_id%5E1', path+'go_complex_terms' ]

exclude_codes = [ 'IEA' ]
pp            = pprint.PrettyPrinter( indent = 4 )
complexes     = dict()

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
        gunzip( files[2], path, files[3] )
        downloadFromUrl( files[1], files[2] )
        gunzip( files[2], path, files[3], True )
        downloadFromUrl( files[4], files[5] ) # get go complex terms

    def _assign( self, ckey, eid, symb, taxid, ref, eco):
        if symb not in complexes[ ckey ]:
            complexes[ckey][ symb ] = { 'pmids' : set(),
                                        'taxid' : taxid,
                                        'eid'   : eid,
                                        'eco'   : set() }
            
            if len(ref) > 0 :
                complexes[ckey][symb]['pmids'].add( ref )
            complexes[ckey][symb]['eco'].add( eco )

    def _load_dbtable( self ):

        Interaction.objects.filter( srcdb = 'GOCOMP' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_translate_file( self ):

        # gaf file format:
        #     http://geneontology.org/page/go-annotation-file-gaf-format-21
        # 
        
        keep      = [1,2,3,4,5,6,12] 
        sp2eid    = { str(x['swissprot']): [ x['symbol'], x['eid']] for x in Entrez.objects.values( 'eid', 'symbol', 'swissprot' )}
        s2eid     = { str(x['symbol']): [ x['symbol'], x['eid']] for x in Entrez.objects.values( 'eid', 'symbol' )}
        s2hgnc    = { str(x['symbol']): [ x['symbol'], x['entrez_id']] for x in Hgnc.objects.values( 'hgnc_id', 'symbol', 'entrez_id' )}
        
        inp       = files[3]
        outp      = final
        go_terms  = dict()

        with open( files[5], 'rt' ) as fhh:
            for line in fhh:
                line      = line.rstrip( )
                fields    = line.split( "\t" )
                go_terms[ fields[0]] = fields[1]
        
        with open( inp, 'rt' ) as fh:
            for line in fh:
                if re.search( r'^!.*', line ): #skip comment lines
                          continue

                line      = line.rstrip( )
                fields    = line.split( "\t" )

                if fields[4] not in go_terms:
                    continue

                if not re.search( '.*complex$', go_terms[fields[4]]) or go_terms[fields[4]] == 'protein complex':
                    continue
                
                if fields[3] != '': # skip qualified terms
                    continue

                if fields[6] in exclude_codes: # skip these evidence codes
                    continue

                taxid     = str(re.sub( r'taxon:', '', fields[12] ))
                # at this point, let's save the complex
                ckey      = go_terms[fields[4]] + '.' + fields[4] + '.' + str(taxid)
                if ckey not in complexes:
                    complexes[ ckey ] = dict()

                ref      = ''
                if re.search( r'PMID:(\d+)$', fields[5] ):
                    ref  = re.sub( r'^.*PMID:(\d+)$', r'\1', fields[5])
                
                if fields[1] in sp2eid:
                    eid  = sp2eid[ fields[1] ][1]
                    symb = sp2eid[ fields[1] ][0]                    
                elif fields[2] in s2hgnc:
                    eid  = s2hgnc[ fields[2] ][1]
                    symb = s2hgnc[ fields[2] ][0]
                elif fields[2] in s2eid:
                    eid  = s2eid[ fields[2] ][1]
                    symb = s2eid[ fields[2] ][0]
                else:
                    eid  = ''
                    symb = fields[2]

                self._assign( ckey, eid, symb, taxid, ref, fields[6] )                    
        #pp.pprint( complexes )
        with open(outp, 'wt') as oh:
            for comp in complexes:
                symbols = [ s for s in complexes[comp] ]
                for i in range( 0, len(symbols)-1 ):
                    for j in range( i+1, len(symbols) ):

                        index = comp + '_' + str(i) + '-' + str(j)
                        print( index + '  ' + str(len(complexes[comp])) )
                        #pp.pprint(complexes[comp])
                        eida  = complexes[comp][ symbols[i] ]['eid']
                        eidb  = complexes[comp][ symbols[j] ]['eid']
                        taxa  = complexes[comp][ symbols[i] ]['taxid']
                        taxb  = complexes[comp][ symbols[j] ]['taxid']
                        eco   = '|'.join( complexes[comp][ symbols[i] ]['eco'] | complexes[comp][ symbols[j] ]['eco'] )
                        pmid  = '|'.join( complexes[comp][ symbols[i] ]['pmids'] | complexes[comp][ symbols[j] ]['pmids'] )
                        
                        # interid, entrezA, B, symbolA, B, taxidA, B, system, systemtype, throughput, score, pmid, source           
                        oh.write( "\t".join([index, str(eida), str(eidb), symbols[i], symbols[j], str(taxa), str(taxb), eco, '', '', '0.0', pmid, 'GOCOMP' ]) + "\n")

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
            print( 'reparse' )
            self._parse_translate_file()
            self._load_dbtable()
        else:
            print('do-over')
            self._download_from_database()
            self._parse_translate_file()
            self._load_dbtable()
            #self._export_ifile() 
