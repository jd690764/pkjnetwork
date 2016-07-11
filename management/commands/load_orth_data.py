from django.core.management.base import BaseCommand
from django.db import connection
import subprocess

import pickle

from lib.fileUtils import downloadFromUrl, gunzip
from network.models import Ensembl
from network.models import Entrez
from network.models import Homologene
from network.models import Enshom

import pprint

pp    = pprint.PrettyPrinter(indent=4, compact=True, depth=2)

path  = 'data/gene/'
path2 = 'data/pickles/'
files = [ 'ftp://ftp.ncbi.nih.gov/pub/HomoloGene/current/homologene.data',
          path+'hg.data',
          path2+'h2m_latest', # hg pickle file
          path2+'m2h_latest', # hg pickle file
          path+'h2m_ens.txt',
          path+'m2h_ens.txt',
          path+'h2m_ens_latest.txt',
          path+'m2h_ens_latest.txt',
          path2+'h2m_ens_latest', # ens pickle file
          path2+'m2h_ens_latest' # ens pickle file
]

def form_query( taxid1, taxid2):
    string = '\n'.join([
        'select CAST(h.eid as CHAR(20)) as heid, CAST(m.eid as CHAR(20)) as meid', 
        'from homologene h, homologene m',
        'where h.hid = m.hid',
        'and h.taxid = ' + str(taxid1),
        'and m.taxid = ' + str(taxid2)
        ])
    #print( string )
    return string    

def ensid2eid( taxid ):
    string = '\n'.join([
        "select substring_index(substring_index(substring_index(external, ';', 2), ';', -1), ':', -1) ensemblid, CAST(eid as CHAR(20)) as eid, symbol",
        'from entrez',
        "WHERE external like '%Ensembl%'",
        'and taxid = ' + str(taxid)
    ])
    #print( string )
    
    cursor       = connection.cursor()
    cursor.execute( string )
    data         = cursor.fetchall()
    d            = dict()
    for line in data:
        #print( str(line[0]) +'\t' + str(line[1]) +'\t' + str(line[2]))
        d[ line[0]] = [line[1], line[2]]
        
    return d


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'
    
    def _download_homology_data( self ):

        downloadFromUrl( files[0], files[1] )
        # download h2m data from biomart
        subprocess.call(['wget', '-O', files[4], 'http://www.ensembl.org/biomart/martservice?query=<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE Query><Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" ><Dataset name = "hsapiens_gene_ensembl" interface = "default" ><Filter name = "with_homolog_mmus" excluded = "0"/><Attribute name = "ensembl_gene_id" /><Attribute name = "mmusculus_homolog_ensembl_gene" /><Attribute name = "mmusculus_homolog_associated_gene_name" /><Attribute name = "mmusculus_homolog_orthology_type" /><Attribute name = "mmusculus_homolog_orthology_confidence" /></Dataset></Query>'])
        # download m2h data from biomart
        subprocess.call(['wget', '-O', files[5], 'http://www.ensembl.org/biomart/martservice?query=<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE Query><Query virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" > <Dataset name = "mmusculus_gene_ensembl" interface = "default" > <Filter name = "with_homolog_hsap" excluded = "0"/> <Attribute name = "ensembl_gene_id" /> <Attribute name = "hsapiens_homolog_ensembl_gene" /> <Attribute name = "hsapiens_homolog_associated_gene_name" /> <Attribute name = "hsapiens_homolog_orthology_type" /> <Attribute name = "hsapiens_homolog_orthology_confidence" /> </Dataset></Query>'])

    def _load_dbtable( self ):

        # load data into homologene table
        Homologene.objects.all().delete()
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.homologene FIELDS TERMINATED BY "\t"' + 
                       ' (HID, TAXID, EID, SYMBOL, PROTGI, PROTACC)', [ files[1] ] )

        Enshom.objects.all().delete()
        with connection.cursor() as c:
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.enshom FIELDS TERMINATED BY "\t"' + 
                       ' (eida, symbola, taxida, eidb, symbolb, taxidb, maptype, certainty)', [ files[6] ] )
            c.execute( 'LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.enshom FIELDS TERMINATED BY "\t"' + 
                       ' (eida, symbola, taxida, eidb, symbolb, taxidb, maptype, certainty)', [ files[7] ] )
            
    def _parse_ens_file( self, infile, outfile, taxid1, taxid2 ):

        # make ensid to entrez map
        ens2eid1 = ensid2eid( taxid1 )
        ens2eid2 = ensid2eid( taxid2 )
           
        # process ensembl data, nothing to do for homologene data
        with open( infile, 'rt' ) as inf:
            with open( outfile, 'wt' ) as outf:
                for line in inf:
                    fields = line.split( '\t' )
                    if fields[0] in ens2eid1 and fields[1] in ens2eid2:
                        outf.write( '\t'.join([ str(ens2eid1[fields[0]][0]), ens2eid1[fields[0]][1], str(taxid1),
                                                str(ens2eid2[fields[1]][0]), ens2eid2[fields[1]][1], str(taxid2),
                                                fields[3], str(fields[4]) ]))


    def _make_pickle( self, taxid1, taxid2, f, stype ):

        cursor       = connection.cursor()
        str_hg       = form_query( taxid1, taxid2 )
        str_ens      = 'select CAST(eida as CHAR(20)) as eida, CAST(eidb as CHAR(20)) as eidb from enshom where taxida = ' + str(taxid1) + ' and taxidb = ' + str(taxid2)
        strg         = ''
        if stype == 'hg':
            strg     = str_hg
        elif stype == 'ens':
            strg     = str_ens
        else: # assume 'all'
            strg     = str_hg + ' union ' + str_ens

        cursor.execute( strg )
        data         = cursor.fetchall()
        d            = dict()

        q            = "select eid, genetype from entrez where genetype = 'protein-coding'"
        cursor.execute( q )
        entrez       = cursor.fetchall()
        cursor.close()
        edict        = {}
        for e, t in entrez:
            edict[str(e)] = str(t)
        
        for heid, meid in data:
            if heid in edict and meid in edict:
                if heid in d:
                    d[ heid ] |= {meid}
                else:
                    d[ heid ]  = { meid }

        pickle.dump( d, open( f, 'wb' ))

            
    def handle(self, *args, **options):
        self._download_homology_data()
        self._parse_ens_file( files[4], files[6], 9606, 10090 )
        self._parse_ens_file( files[5], files[7], 10090, 9606 )
        self._load_dbtable()
        self._make_pickle( 9606, 10090, files[2], 'all' )
        self._make_pickle( 10090, 9606, files[3], 'all' )
