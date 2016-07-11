from django.core.management.base import BaseCommand
from lib import genehasher
from lib.fileUtils import downloadFromUrl
import subprocess
import os
from network.models import Entrez
from django.db import connection

import pickle
from lib import markutils as mu

path  = 'data/gene/'
path2 = 'data/pickles/'
files = { 'hs' : [ 'ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/ASN_BINARY/Mammalia/Homo_sapiens.ags.gz',
                   path+'hs.ags.gz',
                   path+'hs.xml',
                   path+'hs_unmapped.cp2',
                   path2+'hs_unmapped.cp2',                   
                   '9606',
                   path2+'hsg_latest',
                   path2+'hsg_old' ],
          'mm' : [ 'ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/ASN_BINARY/Mammalia/Mus_musculus.ags.gz',
                   path+'mm.ags.gz',
                   path+'mm.xml',
                   path+'mm_unmapped.cp2',
                   path2+'mm_unmapped.cp2',
                   '10090',
                   path2+'mmg_latest',
                   path2+'mmg_old' ]
}
domain_file = path2 + 'gene2dom.cyt'

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_entrez_and_convert( self ):

        for org, f in files.items():
            downloadFromUrl( f[0], f[1] )

            # convert to xml file
            subprocess.call( [path + 'linux64.gene2xml', '-b', '-c', '-i',  f[1],  '-o',  f[2] ])
            os.remove( f[1] )

    def _load_dbtable( self ):

        # load data into entrez table
        Entrez.objects.all().delete()
        with connection.cursor() as c:
            for org, f in files.items():
                c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.entrez FIELDS TERMINATED BY "\t"' + 
                           ' (CDD, EID, EXTERNAL, LOCATION, PEPTIDE, PUBMED, SUMMARY, SWISSPROT, SYMBOL, SYNONYM, TAXID, TREMBL, GENETYPE, MRNA)', [ f[3] ] )
        
            
    def _parse_file( self ):

        for org, f in files.items():

            # call the xml parser
            genehasher.xml2bin( f[2], f[3], 'tsv' )
            #os.remove( inp )
            #os.remove( outp )
            
    def _pickler( self ):

        #os.rename( files['hs'][6], files['hs'][7] )
        #os.rename( files['mm'][6], files['mm'][7] )
        #os.rename( path2 + 'hsmmg_latest', path2 + 'hsmmg_old' )
        
        hobjs    = Entrez.objects.filter( taxid = 9606, genetype = 'protein-coding' )
        mobjs    = Entrez.objects.filter( taxid = 10090, genetype = 'protein-coding' )

        eids     = dict()
        exts     = dict()
        pepts    = dict()
        sps      = dict()
        symbols  = dict()
        synonyms = dict()
        trembls  = dict()
        mrnas    = dict()

        oobjs    = [ hobjs, mobjs ]
        hsg      = dict()
        for i in range(2) :
            print( i )
            for dbo in oobjs[ i ]:
                newobj                = dict()
                # these are unique
                newobj[ 'EID' ]       = str(dbo.eid)
                newobj[ 'Summary' ]   = dbo.summary
                newobj[ 'SwissProt' ] = dbo.swissprot
                newobj[ 'Symbol' ]    = dbo.symbol
                newobj[ 'Taxon' ]     = dbo.taxid
                newobj[ 'TrEMBL' ]    = dbo.trembl
                # these are not...
                
                newobj[ 'mRNA' ]      = dbo.mrna.split( ';' )
                newobj[ 'CDD' ]       = dbo.cdd.split( ';' )
                newobj[ 'External' ]  = dbo.external.split( ';' )
                newobj[ 'Location' ]  = dbo.location.split( ';' )
                newobj[ 'Peptide' ]   = dbo.peptide.split( ';' )
                newobj[ 'Pubmed' ]    = set( dbo.pubmed.split( ';' ) )
                newobj[ 'Synonym' ]   = dbo.synonym.split( ';' )

                # these should be 1 to 1...
                eids[ str(dbo.eid) ]  = newobj
                symbols[ dbo.symbol ] = newobj
                sps[ dbo.swissprot ]  = newobj
                trembls[ dbo.trembl ] = newobj
                # these may not...
                for mrna in newobj[ 'mRNA' ]:
                    if mrna in mrnas:
                        mrnas[ mrna ].append( newobj )
                    else:
                        mrnas[ mrna ] = [ newobj ]
                for syn in newobj[ 'Synonym' ]:
                    if syn in synonyms:
                        synonyms[ syn ].append( newobj )
                    else:
                        synonyms[ syn ] = [ newobj ]
                for pept in newobj[ 'Peptide' ]:
                    if pept in pepts:
                        pepts[ pept ].append( newobj )
                    else:
                        pepts[ pept ] = [ newobj ] 
                for ext in newobj[ 'External' ]:
                    if ext in exts:
                        exts[ ext ].append( newobj )
                    else:
                        exts[ ext ] = [ newobj ]

            to_pickle = { 'EID'      : eids,
                          'External' : exts,
                          'Peptide'  : pepts, 
                          'SwissProt': sps, 
                          'Symbol'   : symbols, 
                          'Synonym'  : synonyms, 
                          'TrEMBL'   : trembls, 
                          'mRNA'     : mrnas }
            if i == 0:
                pickle.dump( to_pickle, open( files[ 'hs' ][6], 'wb' ))
                print( len(to_pickle['EID']))
                import copy
                hsg   = copy.deepcopy(to_pickle)

            elif i == 1:
                pickle.dump( to_pickle, open( files[ 'mm' ][6], 'wb' ))
                print( len(to_pickle['EID']))
                for eid in hsg['EID']:
                    print( eid )
                    to_pickle['EID'][eid] = hsg['EID'][eid] 
                for ext in hsg['External']:
                    print(ext)
                    to_pickle['External'][ext] = hsg['External'][ext]

                for pept in hsg['Peptide']:
                    print(pept)
                    to_pickle[ 'Peptide' ][pept] = hsg[ 'Peptide' ][pept]

                for sp in hsg['SwissProt']:
                    print(sp)
                    to_pickle[ 'SwissProt' ][sp] = hsg[ 'SwissProt' ][sp]

                for sym in hsg['Symbol']:
                    print(sym)
                    to_pickle['Symbol'][sym] = hsg['Symbol'][sym]

                for syn in hsg['Synonym']:
                    print(syn)
                    if syn in to_pickle['Synonym']:
                        to_pickle['Synonym'][syn].append( hsg['Synonym'][syn])
                    else:
                        to_pickle['Synonym'][syn] = hsg['Synonym'][syn]
                
                for tr in hsg['TrEMBL']:
                    print(tr)
                    to_pickle[ 'TrEMBL' ][tr] = hsg[ 'TrEMBL' ][tr]

                for mrna in hsg['mRNA']:
                    print(mrna)
                    to_pickle[ 'mRNA' ][mrna] = hsg[ 'mRNA' ][mrna]
                    
                print( len(hsg['EID']))
                print( len(to_pickle['EID']))
                pickle.dump( to_pickle, open( path2 + 'hsmmg_latest', 'wb' ))

    def _export_domain_file( self ):
        sql = '\n'.join(["select symbol, group_concat(distinct cdd.name SEPARATOR ' | ') names, group_concat(distinct case when length(substring_index(substring_index(description, '.', 1), ';', 1)) > 50 then concat(substring(description, 1, 50), '...') else substring_index(substring_index(description, '.', 1), ';', 1) end separator ' | ') descriptions",
                        "from (", 
                        "select", 
                        "entrez.symbol,",
                        "SUBSTRING_INDEX(SUBSTRING_INDEX(entrez.cdd, ';', numbers.n), ';', -1) domain",
                        "from",
                        "numbers inner join entrez",
                        "on CHAR_LENGTH(entrez.cdd)",
                        "-CHAR_LENGTH(REPLACE(entrez.cdd, ';', ''))>=numbers.n-1",
                        "order by",
                        "symbol, domain",
                        ") x,", 
                        "cdd",
                        "where x.domain is not null",
                        "and x.domain <> ''",
                        "and x.domain = cdd.pssm",
                        "group by x.symbol"])
        print( sql )

        with connection.cursor() as c:
            c.execute( sql )
            data = c.fetchall()

        with open(domain_file, 'wt') as df:
            for ( symb, doms, descs ) in data:
                df.write( '\t'.join( [symb, doms, descs] ) + '\n')
        
            
    def handle(self, *args, **options):
        #self._download_from_entrez_and_convert()
        #self._parse_file()
        #self._load_dbtable()
        #self._pickler()
        self._export_domain_file()
