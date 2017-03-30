from django.core.management.base import BaseCommand
from os import listdir
from os.path import isfile, join
import gzip
import re
from lib.fileUtils import downloadFromUrl
from network.models import Uniprot
from django.db import connection
import subprocess
import datetime

path  = 'data/protein/'

files = [ 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping_selected.tab.gz',
          'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/MOUSE_10090_idmapping_selected.tab.gz',
          path + 'hs_uniprot.gz',
          path + 'mm_uniprot.gz',
          path + 'uniprot_latest' ]

class Command(BaseCommand):
    args = '<foo bar ...>'
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
    
    def _download_from_uniprot( self ):
        # download files from ftp site
        subprocess.call([ 'wget', '-q', files[0], '-O', files[2] ])
        subprocess.call([ 'wget', '-q', files[1], '-O', files[3] ])
                          
    def _parse_downloaded_files( self ):

        with open( files[4], 'wt' ) as outf:

            maxeid    = 0
            maxrsid   = 0
            maxomim   = 0
            maxpmid   = 0
            maxensid  = 0
            maxenspid = 0            

            for i in range(2,4,1):
                gz = files[i]
                with gzip.open( gz, 'rt' ) as inf:
                    # 1. UniProtKB-AC
                    # 2. UniProtKB-ID
                    # 3. GeneID (EntrezGene)
                    # 4. RefSeq
                    # 5. GI
                    # 6. PDB
                    # 7. GO
                    # 8. UniRef100
                    # 9. UniRef90
                    # 10. UniRef50
                    # 11. UniParc
                    # 12. PIR
                    # 13. NCBI-taxon
                    # 14. MIM
                    # 15. UniGene
                    # 16. PubMed
                    # 17. EMBL
                    # 18. EMBL-CDS
                    # 19. Ensembl
                    # 20. Ensembl_TRS
                    # 21. Ensembl_PRO
                    # 22. Additional PubMed

                    # only keep: 0, 1, 2, 3, 12, 13, 15, 18, 20

                    for line in inf:                        

                        line      = line.strip( )
                        line      = re.sub( "; ", ";", line )
                        line      = re.sub( ';\t', '\t', line )

                        fields    = line.split( '\t' )
                        #print('+'.join(fields) + '\n')
                        index     = len(fields)
                        eid       = fields[2] if index > 2 else 'None'
                        rsid      = fields[3] if index > 3 else 'None'
                        rsid      = re.sub( r'([XNY]P_\d+)\.\d+', r'\1', rsid )
                        taxid     = fields[12] if index > 12 else 'None'
                        omim      = fields[13] if index > 13 else 'None'
                        pmid      = fields[15] if index > 15 else 'None'
                        ensid     = fields[18] if index > 18 else 'None'
                        enspid    = fields[20] if index > 20 else 'None'
                        outf.write( '\t'.join([ fields[0], fields[1], eid, rsid, taxid, omim, pmid, ensid, enspid ]) + '\n' )                        
                        maxeid    = len(eid) if len(eid) > maxeid else maxeid
                        maxrsid   = len(rsid) if len(rsid) > maxrsid else maxrsid
                        maxomim   = len(omim) if len(omim) > maxomim else maxomim
                        maxpmid   = len(pmid) if len(pmid) > maxpmid else maxpmid
                        maxensid  = len(ensid) if len(ensid) > maxensid else maxensid
                        maxenspid = len(enspid) if len(enspid) > maxenspid else maxenspid

            print( 'maxeid: ' + str(maxeid) + '\nmaxrsid: ' + str(maxrsid) + '\nmaxomim: ' + str(maxomim) + '\nmaxpmid: ' + str(maxpmid) + '\nmaxensid: ' + str(maxensid) + '\nmaxenspid: ' + str(maxenspid) + '\n' )
        
    def _load_dbtable( self ):

        # load data into entrez table
        Uniprot.objects.all().delete()
        with connection.cursor() as c:
            c.execute( "LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.uniprot FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '\"' " + 
                       '(upacc, upid, @var1, @var2, taxid, @var3, @var4, @var5, @var6) ' +
                       'SET eid      = case when @var1 = "None" or @var1 = "" then NULL else @var1 end, ' +
                       'refseqid     = case when @var2 = "None" or @var2 = "" then NULL else @var2 end, ' +
                       'omim         = case when @var3 = "None" or @var3 = "" then NULL else @var3 end, ' +
                       'pmid         = case when @var4 = "None" or @var4 = "" then NULL else @var4 end, ' +                       
                       'ensid        = case when @var5 = "None" or @var5 = "" then NULL else @var5 end, ' +
                       'enspid       = case when @var6 = "None" or @var6 = "" then NULL else @var6 end; ' 
                       , [ files[4] ] )
            c.execute( 'ALTER TABLE uniprot ADD INDEX upacc_i (upacc );' )
            c.execute( 'ALTER TABLE uniprot ADD INDEX upid_i (upid );' )
            c.execute( 'ALTER TABLE uniprot ADD INDEX eid_i (eid );' )                        

            
        
    def handle(self, *args, **options):
        print( '\n\n\n\n############################ ' + 'update uniprot data on ' + str(datetime.date.today()))
        if options[ 'reload' ]:
            self._load_dbtable()
        elif options[ 'reparse' ]:
            self._parse_downloaded_files()
            self._load_dbtable()
        else:
            self._download_from_uniprot()
            self._parse_downloaded_files()
            self._load_dbtable()
