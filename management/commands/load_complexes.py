import os
import re

from django.db import connection
from django.core.management.base import BaseCommand

import pyexcel as pe

from network.models import Interaction, Entrez
from lib.fileUtils import downloadFromUrl
from lib import config as cf

import pprint

path       = 'data/interactions/'
final      = path+'complexes_latest'
ifile      = cf.complexPath
byGeneFile = cf.complexByGeneFile
files      = [ path + 'complexes_local.txt' ]

pp         = pprint.PrettyPrinter( indent = 4 )

# query for ifile
sqli       = """
select 
        concat(replace(interid, concat('.', substring_index(interid, '.', -2)), ''), '_', substring_index(interid, '_', -1)) interid, 
        entreza, 
        entrezb, 
        symbola, 
        symbolb, 
        organisma,
        group_concat(substring_index(substring_index(interid, '.', -2), '.', 1)) ids
from interaction
where srcdb = 'COMPLEXES'
group by 1, 6
order by 6, 1"""

# query for by_gene_file
sqlby      = """
select 
    symbola, 
    group_concat(distinct complex order by complex SEPARATOR '|') complex, 
    group_concat(distinct ids SEPARATOR '|') ids, taxid 
from (
    select symbola, substring_index(interid, '.', 1) complex, substring_index(replace(interid, concat('_',substring_index(interid, '_', -1)), ''), '.', -2) ids, substring_index(replace(interid, concat('_',substring_index(interid, '_', -1)), ''), '.', -1) taxid
    from interaction
    where srcdb = 'COMPLEXES'

    union

    select symbolb, substring_index(interid, '.', 1) complex, substring_index(replace(interid, concat('_',substring_index(interid, '_', -1)), ''), '.', -2) ids, substring_index(replace(interid, concat('_',substring_index(interid, '_', -1)), ''), '.', -1) taxid
    from interaction
    where srcdb = 'COMPLEXES'
) x
group by symbola, taxid
"""

# select interactions to create complexes
sqlq       = """
select complex, subunits, source, \"m\" as \"unique\" from (         
        select complex, group_concat(symbola order by symbola) subunits, \"gocomp\" source from
        ( 
                select substring_index(interid, '_', 1) complex, symbola, organisma 
                from interaction
                where srcdb = 'GOCOMP'
                
                union
                
                select substring_index(interid, '_', 1) complex, symbolb, organisma
                from interaction
                where srcdb = 'GOCOMP'
        ) x
        group by complex

        union

        select complex, group_concat(symbola order by symbola) subunits, \"intcomp\" source from
        ( 
                select substring_index(interid, '_', 1) complex, symbola, organisma 
                from interaction
                where srcdb = 'INTCOMP'
                
                union
                
                select substring_index(interid, '_', 1) complex, symbolb, organisma
                from interaction
                where srcdb = 'INTCOMP'
        ) x
        group by complex

        union
        
        select complex, group_concat(symbola order by symbola) subunits, \"corum\" source from
        ( 
                select substring_index(interid, '_', 1) complex, symbola, organisma 
                from interaction
                where srcdb = 'CORUM'
                
                union
                
                select substring_index(interid, '_', 1) complex, symbolb, organisma
                from interaction
                where srcdb = 'CORUM'
        ) x
        group by complex

        union
        
        select complex, group_concat(symbola order by symbola) subunits, \"emili\" source from
        ( 
                select substring_index(interid, '_', 2) complex, symbola, organisma 
                from interaction
                where srcdb = 'EMILI'
                
                union
                
                select substring_index(interid, '_', 2) complex, symbolb, organisma
                from interaction
                where srcdb = 'EMILI'
        ) x
        group by complex
) z
where subunits in (
        select subunits from (
                select complex, group_concat(symbola order by symbola) subunits, \"emili\" source from
                ( 
                        select substring_index(interid, '_', 2) complex, symbola, organisma 
                        from interaction
                        where srcdb = 'EMILI'
                        
                        union
                        
                        select substring_index(interid, '_', 2) complex, symbolb, organisma
                        from interaction
                        where srcdb = 'EMILI'
                ) x
                group by complex
                
                union
                
                select complex, group_concat(symbola order by symbola) subunits, \"corum\" source from
                ( 
                        select substring_index(interid, '_', 1) complex, symbola, organisma 
                        from interaction
                        where srcdb = 'CORUM'
                        
                        union
                        
                        select substring_index(interid, '_', 1) complex, symbolb, organisma
                        from interaction
                        where srcdb = 'CORUM'
                ) x
                group by complex
                
                union
                
                select complex, group_concat(symbola order by symbola) subunits, \"intcomp\" source from
                ( 
                        select substring_index(interid, '_', 1) complex, symbola, organisma 
                        from interaction
                        where srcdb = 'INTCOMP'
                        
                        union
                        
                        select substring_index(interid, '_', 1) complex, symbolb, organisma
                        from interaction
                        where srcdb = 'INTCOMP'
                ) x
                group by complex
                
                union
                
                select complex, group_concat(symbola order by symbola) subunits, \"gocomp\" source from
                ( 
                        select substring_index(interid, '_', 1) complex, symbola, organisma 
                        from interaction
                        where srcdb = 'GOCOMP'
                        
                        union
                        
                        select substring_index(interid, '_', 1) complex, symbolb, organisma
                        from interaction
                        where srcdb = 'GOCOMP'
                ) x
                group by complex
        ) y
        group by subunits
        having count(*) > 1
)

union

select complex, subunits, source, \"1\" as \"unique\" from (
        select complex, group_concat(symbola order by symbola) subunits, \"emili\" source from
        ( 
                select substring_index(interid, '_', 2) complex, symbola, organisma 
                from interaction
                where srcdb = 'EMILI'
                
                union
                
                select substring_index(interid, '_', 2) complex, symbolb, organisma
                from interaction
                where srcdb = 'EMILI'
        ) x
        group by complex
        
        union
        
        select complex, group_concat(symbola order by symbola) subunits, \"corum\" source from
        ( 
                select substring_index(interid, '_', 1) complex, symbola, organisma 
                from interaction
                where srcdb = 'CORUM'
                
                union
                
                select substring_index(interid, '_', 1) complex, symbolb, organisma
                from interaction
                where srcdb = 'CORUM'
        ) x
        group by complex
        
        union
        
        select complex, group_concat(symbola order by symbola) subunits, \"intcomp\" source from
        ( 
                select substring_index(interid, '_', 1) complex, symbola, organisma 
                from interaction
                where srcdb = 'INTCOMP'
                
                union
                
                select substring_index(interid, '_', 1) complex, symbolb, organisma
                from interaction
                where srcdb = 'INTCOMP'
        ) x
        group by complex
        
        union
        
        select complex, group_concat(symbola order by symbola) subunits, \"gocomp\" source from
        ( 
                select substring_index(interid, '_', 1) complex, symbola, organisma 
                from interaction
                where srcdb = 'GOCOMP'
                
                union
                
                select substring_index(interid, '_', 1) complex, symbolb, organisma
                from interaction
                where srcdb = 'GOCOMP'
        ) x
        group by complex
) z
where subunits not in (
        select subunits from (
                select complex, group_concat(symbola order by symbola) subunits, \"emili\" source from
                ( 
                        select substring_index(interid, '_', 2) complex, symbola, organisma 
                        from interaction
                        where srcdb = 'EMILI'
                        
                        union
                        
                        select substring_index(interid, '_', 2) complex, symbolb, organisma
                        from interaction
                        where srcdb = 'EMILI'
                ) x
                group by complex
                
                union
                
                select complex, group_concat(symbola order by symbola) subunits, \"corum\" source from
                ( 
                        select substring_index(interid, '_', 1) complex, symbola, organisma 
                        from interaction
                        where srcdb = 'CORUM'
                        
                        union
                        
                        select substring_index(interid, '_', 1) complex, symbolb, organisma
                        from interaction
                        where srcdb = 'CORUM'
                ) x
                group by complex
                
                union
                
                select complex, group_concat(symbola order by symbola) subunits, \"intcomp\" source from
                ( 
                        select substring_index(interid, '_', 1) complex, symbola, organisma 
                        from interaction
                        where srcdb = 'INTCOMP'
                        
                        union
                        
                        select substring_index(interid, '_', 1) complex, symbolb, organisma
                        from interaction
                        where srcdb = 'INTCOMP'
                ) x
                group by complex
                
                union
                
                select complex, group_concat(symbola order by symbola) subunits, \"gocomp\" source from
                ( 
                        select substring_index(interid, '_', 1) complex, symbola, organisma 
                        from interaction
                        where srcdb = 'GOCOMP'
                        
                        union
                        
                        select substring_index(interid, '_', 1) complex, symbolb, organisma
                        from interaction
                        where srcdb = 'GOCOMP'
                ) x
                group by complex
        ) y
        group by subunits
        having count(*) > 1
)"""

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
            '--reexport',
            action  = 'store_true',
            dest    = 'reexport',
            default = False,
            help    = 'Reexport ifile and do nothing else',
        )
        parser.add_argument(
            '--reparse',
            action  = 'store_true',
            dest    = 'reparse',
            default = False,
            help    = 'Reparse previously downloaded data and reload table',
        )
    
    def _load_dbtable( self ):

        Interaction.objects.filter( srcdb = 'COMPLEXES' ).delete()
        
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.interaction FIELDS TERMINATED BY "\t" ' +
                       '(INTERID, ENTREZA, ENTREZB, SYMBOLA, SYMBOLB, ORGANISMA, ORGANISMB, SYSTEM, SYSTEMTYPE, THROUGHPUT, SCORE, SRCDB, pmid)', [final] )
       
    def _parse_translate_file( self ):

        # columns are:
        # 0 - name of complex
        # 1 - original id of complex
        # 2 - taxid
        # 3 - gene symbols (separated by ',')
        # 4 - name to use
        # 5 - souce of complex info
        # 6 - '1' if the gene symbols string is unique
        #     'm' if it is not (case insensitive)
        
        entrez   = { x['symbol']: [ x['symbol'], x['eid'] ] for x in Entrez.objects.values( 'eid', 'symbol' )}
        #pp.pprint( entrez )
        inp      = files[0]
        outp     = final
        interids = dict()
        eids     = dict()
        indeces  = dict()
                     
        
        # very little to do
        with open( inp, 'rt' ) as f:
            for line in f:

                # skip if header
                if re.search( '^complex.*', line ):
                    continue

                line      = line.rstrip( )
                fields    = line.split( '\t' )
                #fields[1] = re.sub( '\t', ' ', fields[1])
                symbs     = fields[3].split( ',' )

                for symb in symbs :
                    if symb in entrez:
                        eids[ symb ] = entrez[ symb ][1]
                    else:
                        print(str(symb) + ' is not in entrez')
                        eids[ symb ] = symb 

                for i in range( 0, len(symbs)-1 ):
                    for j in range( 1, len(symbs) ):
                        index            = fields[0] + '.'  + str(fields[1]) + '.' + str(fields[2]) + '_' + symbs[i] + '-' + symbs[j]
                        indeces[ index ] = fields[4] + '.'  + str(fields[1]) + '.' + str(fields[2])

        with open(outp, 'wt') as oh:
            with connection.cursor() as c:
            # very long query, be patient ... (6-7 minutes)
                c.execute( sqlq )
                for row in c.fetchall():
                    symbs = row[1].split( ',' )
                    m     = re.match( r'^(.+)\.([^\.]+)\.([^\.]+)$', row[0] )
                    print( row[0] )
                    if m is None :
                        taxid = '9606'
                        indx  = row[0] + '.' + row[0] + '.' + taxid
                    else :
                        taxid = m.group(3)
                        indx  = row[0]
                    for i in range( 0, len(symbs)-1 ):
                        for j in range( i+1, len(symbs) ):
                            ind = indx + '_' + symbs[i] + '-' + symbs[j]
                            if ind in indeces:
                                ied = indeces[ind] + '_' + str(i) + '-' + str(j) 
                                oh.write( '\t'.join([ ied, str(eids[symbs[i]]), str(eids[symbs[j]]), symbs[i], symbs[j], str(taxid), str(taxid), '', '', '', '0.0', 'COMPLEXES', ''  ]) + '\n' )
                            else :
                                for k in [i, j]:
                                    if symbs[k] not in eids:
                                        if symbs[k] in entrez:
                                            eids[ symbs[k] ] = entrez[ symbs[k] ][1]
                                        else:
                                            print(str(symbs[k]) + ' is not in entrez')
                                            eids[ symbs[k] ] = symbs[k]
                                        
                                ied = indx + '_' + str(i) + '-' + str(j)
                                oh.write( '\t'.join([ ied, str(eids[symbs[i]]), str(eids[symbs[j]]), symbs[i], symbs[j], str(taxid), str(taxid), '', '', '', '0.0', 'COMPLEXES', ''  ]) + '\n' )
                
                            
    def _export_ifile( self ):

        with open(ifile, 'wt') as oh:
            oh.write( '\t'.join([ 'interID', 'entrezA', 'entrezB', 'biogridA', 'biogridB', 'systematicA', 'systematicB', 'officialA', 'officialB', 'synonymsA', 'synonymsB', "system" , "systemType" , "Author" , "pmid" , 'organismA', 'organismB', "throughput" , "score" , "modification" , "phenotypes", "qualifications" , "tags" , "srcDB" ]) + '\n' )
            with connection.cursor() as c:
                c.execute( sqli )
                for row in c.fetchall():
                    oh.write('\t'.join( [row[0], str(row[1]), str(row[2]), '', '', '', '', row[3], row[4], '', '', '', '', '', '', str(row[5]), str(row[5]), '', '', '', '', '', '', row[6]] ) + '\n')


    def _export_byGeneFile( self ):
        with open(byGeneFile, 'wt') as oh:
            oh.write( '\t'.join([ 'symbol', 'complex', 'ids', 'taxid' ]) + '\n' )
            with connection.cursor() as c:
                c.execute( sqlby )
                for row in c.fetchall():
                    oh.write('\t'.join( [row[0], row[1], row[2], str(row[3])] ) + '\n')

                    
    def handle(self, *args, **options):
        if options[ 'reload' ]:
            print('reload')
            self._load_dbtable()
            self._export_ifile()
            self._export_byGeneFile()            
        elif options[ 'reparse' ]:
            self._parse_translate_file()
            self._load_dbtable()
            self._export_ifile()
            self._export_byGeneFile()            
        elif options[ 'reexport' ]:
            self._export_ifile()
            self._export_byGeneFile()            
        else:
            print('redo')
            self._parse_translate_file()
            self._load_dbtable()
            self._export_ifile()
            self._export_byGeneFile()
