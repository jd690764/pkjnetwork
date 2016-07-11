import os
import re

from django.db import connection
from django.core.management.base import BaseCommand

import pyexcel as pe
import pyexcel.ext.xlsx

from network.models import Entrez, Syns_view, Hgnc, Interaction, Ensembl
from lib.fileUtils import unzip, downloadFromUrl

import pprint

path   = 'data/interactions/'
final  = path+'emiliome_data_v2_latest'
files  = [ [ path+'emiliome_v2_suppl2.xlsx', path+'emiliome_v2_suppl2.tsv', '16655 PPIs with evidence'], # this file contains the actual interaction data
           [ path+'emiliome_v2_suppl4.xlsx', path+'emiliome_v2_suppl4.tsv', 'Hs_2sp_v35.6_981cxs_complexes'] ] # this file contains the clusters (complexes)

srcdb  = 'EMILIv2'

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_labsite( self ):
        ###################
        # the files were downloaded from the journal website as
        # supplemental tables 2 & 4. These files are the ones in
        # files and the corresponding sheets contain the relevant data
        # 
        
            # extract appropriate sheet
        for f in files:
            print( f[0] )
            book = pe.get_book( file_name = f[0] )
            print( f[2])
            book[ f[2] ].save_as( f[1] )

            
    def _load_dbtable( self ):
        Interaction.objects.filter( srcdb = srcdb ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t"', [final] )

            
    def _parse_translate_file( self ):

        # lookup symbols in entrez, hgnc symbols and their synonyms
        entrez     = Entrez.objects.filter( taxid = 9606 ).values( 'eid', 'symbol', 'external'  )
        genedict   = {}
        for dic in entrez:
            genedict[ dic['symbol'].upper() ]          = str(dic['eid'])
            genedict[ str(dic['eid']) ]                = dic['symbol']
            genedict[ dic['external'] ]                = dic['symbol']

        hgnc       = Hgnc.objects.filter( entrez_id__isnull = False ).values( 'entrez_id', 'hgnc_id', 'symbol' )
        hgncdict   = {}
        for dic in hgnc:
            if str(dic['entrez_id']) in genedict:
                hgncdict[ dic['symbol'].upper() ]      = genedict[ str(dic['entrez_id']) ] # hgnc symbol => entrez_symbol  
                hgncdict[ dic['hgnc_id'] ]             = genedict[ str(dic['entrez_id']) ] # hgnc_id => entrez_symbol  
            
        syns       = Syns_view.objects.all( ).values( 'eid', 'synonym', 'source' )
        synsdict   = {}
        for dic in syns:
            if dic['source'] == 'entrez':
                if dic['eid'] in genedict:
                    synsdict[ dic['synonym'].upper() ] = genedict[ dic['eid']] # entrez syn => entrez_symbol
            else:
                if dic['eid'] in hgncdict:
                    synsdict[ dic['synonym'].upper() ] = hgncdict[ dic['eid']] # hgnc syn => entrez_symbol

        ensembl    = Ensembl.objects.filter( taxid     = 9606 ).values( 'ensid', 'gname'  )
        ensdict    = {}
        for dic in ensembl:
            ensdict[ dic['ensid'] ]                    = dic['gname'].upper()                    
                    
        sup2       = list()

        # this file contains the actual interaction data
        # column indexes to keep
        # but first we need to update the symbols, because they are not
        # always correct...
        keep       = [2,3,4,9] # symbola, symbolb, score, hs_interaction
        print( files[0][1] )
        with open( files[0][1] ) as f:
            for line in f:
                # find the entrez symbols/eids
                fields = line.rstrip( '\n' ).split( "\t" )
                # update ens gene symbols
                if fields[0] in ensdict:
                    fields[2] = ensdict[ fields[0] ]
                if fields[1] in ensdict:
                    fields[3] = ensdict[ fields[1] ]

                fields = [ fields[i] for i in keep ]
                if fields[0] == 'ENSG1':
                    pass
                skip   = False
                # update gene symbols in the interaction file
                for i in [ 0, 1 ]:
                    if fields[i] in genedict:
                        pass # all is fine
                    elif fields[i] in hgncdict:
                        fields[i] = hgncdict[ fields[i] ]
                    elif fields[i] in synsdict:
                        fields[i] = synsdict[ fields[i] ]
                    else:
                        print( fields[i] + ' cannot be mapped to entrez.')
                        skip = True
                if not skip:
                    idstr  = '_' + fields[0] + '_' + fields[1] + '_'
                    fields.append( idstr )
                    sup2.append( fields )
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint( sup2 )
        throughput = ''
        organisma  = '9606'
        organismb  = '9606'
        pmid       = '26344197'

        inp        = files[1][1] # this file contains the clusters (complexes)
        outp       = final
        
        with open(outp, 'wt') as oh:
            with open( inp, 'rt' ) as f:
                for line in f:
                    # skip line if header
                    if re.search( '^ComplexID.*', line ):
                        continue

                    # for each complex...                    
                    fields  = line.rstrip( ).split( "\t" )

                    # the fields are complexid, no of subunits, ensids, symbols
                    es      = fields[2].split( ';' )
                    ss      = [''] * len( es )

                    # upate the genes in the complex to current entrez symbol
                    # get the ensembl-ids
                    for i, e in enumerate(es):
                        #print( e )
                        if e in ensdict:
                            ss[ i ] = ensdict[ e ]
                        else:
                            print( e + ' is not in ENSEMBL'

                    symbols = [''] * len( es )
                    for i, s in enumerate(ss):
                        #print(s)
                        if s and s in genedict:
                            symbols[ i ] = s
                            #print( 'genedict' )
                        elif s and s.upper() in hgncdict:
                            symbols[ i ] = hgncdict[ s.upper() ]
                            #print( 'hgncdict' )
                        elif s and s.upper() in synsdict:
                            symbols[ i ] = synsdict[ s.upper() ]
                            #print( 'syn' )

                    print( symbols )
                    if '' in  symbols:
                        print( fields[0] + '\t' + str(len(es)) + '\t' + str(len(symbols)) )
                    #print( symbols )
                            
                    # do the permutations within the complex for each gene pair
                    # and keep the ones where there is some experimental evidence
                    # for the interaction
                    # there are more interactions, but these did not make it into
                    # complexes
                    for i in range( 0, len(symbols)-1 ):
                        for j in range( i+1, len(symbols) ):
                            interid    = 'Cv2_' + fields[0] + '_' + str(i) + '_' + str(j)
                            symbola    = symbols[i]
                            symbolb    = symbols[j]
                            #print( symbola + '\t' + symbolb )
                            entreza    = str(genedict[ symbola.upper() ])
                            entrezb    = str(genedict[ symbolb.upper() ])
                            system     = 'co-fractionation'
                            systemtype = 'physical'
                            
                            for r in sup2:
                                #print( symbola + '\t' + symbolb + str(r) )
                                if re.match( '.*_'+symbola.upper()+'_.*', r[4] ) and re.match( '.*_'+symbolb.upper()+'_.*', r[4] ):
                                    #print( 'match' + str(r) )
                                    score    = str( r[2])
                                    if r[3] == '':
                                        # in these cases there is no direct evidence for
                                        # physical interaction in the human case - there
                                        # is in other organisms
                                        system     = 'co-fractionation (predicted)'
                                        
                                    oh.write( "\t".join([interid, entreza, entrezb, symbola, symbolb, organisma, organismb, system, systemtype, throughput, score, pmid, srcdb ]) + "\n")
                                    break
                                else:
                                    if len(es) == len(symbols):
                                        score  = ''
                                        system = 'co-fractionation (predicted)'
                                        oh.write( "\t".join([interid, entreza, entrezb, symbola, symbolb, organisma, organismb, system, systemtype, throughput, score, pmid, srcdb ]) + "\n")
    def handle(self, *args, **options):
        #self._download_from_labsite()
        self._parse_translate_file()
        self._load_dbtable()
