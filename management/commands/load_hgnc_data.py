from django.core.management.base import BaseCommand
from lib.fileUtils import downloadFromUrl
from network.models import Hgnc
from django.db import connection

path  = 'data/gene/'

files = [ 'ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt',
          path+'hgnc_latest' ]

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _download_from_hugo( self ):
        downloadFromUrl( files[0], files[1] )

    def _load_dbtable( self ):

        # load data into entrez table
        Hgnc.objects.all().delete()
        with connection.cursor() as c:
            c.execute( "LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.hgnc FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '\"' ignore 1 lines " + 
                       '(hgnc_id, symbol, hgnc_name, locus_group, locus_type, status, location, location_sortable, @aka, alias_name, @paka, prev_name, ' +
                       'gene_family, gene_family_id, @var1, @var2, @var3, @var4, @var5, ensembl_gene_id, vega_id, ucsc_id, ena, refseq_accession, ccds_id, ' +
                       'uniprot_ids, pubmed_id, mgd_id, rgd_id, lsdb, cosmic, omim_id, mirbase, homeodb, snornabase, bioparadigms_slc, orphanet, pseudogene, ' +
                       'horde_id, merops, imgt, iuphar, kznf_gene_catalog, mamit_trnadb, cd, lncrnadb, enzyme_id, intermediate_filament_db) ' +
                       'SET date_approved_reserved = STR_TO_DATE(@var1, "%%Y-%%m-%%d"), ' +
                       'date_symbol_changed    = case when @var2 = "" then NULL else STR_TO_DATE(@var2, "%%Y-%%m-%%d") end, ' +
                       'date_name_changed      = case when @var3 = "" then NULL else STR_TO_DATE(@var3, "%%Y-%%m-%%d") end, ' +
                       'date_modified          = case when @var4 = "" then NULL else STR_TO_DATE(@var4, "%%Y-%%m-%%d") end, ' +
                       'entrez_id              = case when @var5 = "" then NULL else @var5 end, ' +
                       'alias_symbol           = case when @aka  = "" then NULL else @aka end, ' +
                       'prev_symbol            = case when @paka = "" then NULL else @paka end;', [ files[1] ] )

            
    def _parse_file( self ):
        pass # nothing to do here
            
        
    def handle(self, *args, **options):
        self._download_from_hugo()
        #self._parse_file()
        self._load_dbtable()
