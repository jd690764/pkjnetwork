import os

from django.core.management.base import BaseCommand
from django.db import connection

from lib import genehasher
from lib.fileUtils import downloadFromUrl, gunzip
from network.models import Ncbiprot

import pickle
import pprint

pp    = pprint.PrettyPrinter(indent=4)
path  = 'data/protein/'
path1 = 'data/pickles/'

files = { 'hs' : [ 'ftp://ftp.ncbi.nlm.nih.gov/genomes/Homo_sapiens/protein/protein.gbk.gz',
                   path + 'hs.protein.gbk.gz',
                   path + 'hs.protein.gbk',
                   path + 'hs.protein.tsv',
                   '9606',
                   path1 + 'hsp_latest' ],
          'mm' : [ 'ftp://ftp.ncbi.nlm.nih.gov/genomes/Mus_musculus/protein/protein.gbk.gz',
                   path + 'mm.protein.gbk.gz',
                   path + 'mm.protein.gbk',                   
                   path + 'mm.protein.tsv',
                   '10090',
                   path1 + 'mmp_latest' ]
}

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_ncbi( self ):

        for org, f in files.items():
            downloadFromUrl( f[0], f[1] )
            gunzip( f[1], path, f[2] )
            os.remove( f[1] )

    def _load_dbtable( self ):

        # load data into protein table
        Ncbiprot.objects.all().delete()
        with connection.cursor() as c:
            for org, f in files.items():
                c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.ncbiprot FIELDS TERMINATED BY "\t" ignore 1 lines' + 
                           ' (ACC, CDS, PROTNAME, EID, GI, LEN, SEQ, SYMBOL, MRNA, TAXID)', [ f[3] ] )

    def _pickler( self ):

        for (org, f) in files.items():

            pobj      = Ncbiprot.objects.filter( taxid = f[4] )

            accs      = dict()
            gis       = dict()
            mrnas     = dict()
            eids      = dict()
            syms      = dict()

            to_pickle = dict()
            
            for po in pobj:
                obj             = dict()                
                obj[ 'Acc' ]    = po.acc
                obj[ 'CDs' ]    = po.cds
                obj[ 'Def' ]    = po.protname
                obj[ 'EID' ]    = str(po.eid)
                obj[ 'GI' ]     = po.gi
                obj[ 'Length' ] = po.len
                obj[ 'Seq' ]    = po.seq
                obj[ 'Sym' ]    = po.symbol
                obj[ 'mRNA' ]   = po.mrna

                accs[po.acc]    = obj
                gis[po.gi]      = obj
                mrnas[po.mrna]  = obj
                if po.eid in eids:
                    eids[po.eid].append( obj )
                else:
                    eids[po.eid] = [ obj ]
                if po.symbol in syms:
                    syms[po.symbol].append( obj )
                else:
                    syms[po.symbol] = [ obj ]

            to_pickle = { 'Acc'  : accs,
                          'EID'  : eids,
                          'GI'   : gis,
                          'Sym'  : syms,
                          'mRNA' : mrnas }
            pickle.dump( to_pickle, open( f[5], 'wb' ))
            
    def _parse_file( self ):

        for org, f in files.items():

            # call the parser
            result = genehasher.parse( f[2] )
            with open( f[3], 'wt' ) as outh:
                keys = sorted( result[0].keys() )
                keys.append( 'taxid' )
                outh.writelines( '\t'.join( keys ) + '\n' )
                for r in result:
                    line = ''
                    for k in sorted( r.keys() ):
                        if( r[k] ):
                            line += str(r[k]) + "\t"
                        else:
                            line += "\t"
                    line += f[4] + '\n'
                    outh.writelines( line )
            
        
    def handle(self, *args, **options):
        self._download_from_ncbi()
        self._parse_file()
        self._load_dbtable()
        self._pickler()
