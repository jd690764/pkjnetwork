from django.core.management.base import BaseCommand
from os import listdir
from os.path import isfile, join
import gzip
import re
from lib.fileUtils import downloadFromUrl, gunzip
from network.models import Uniprot, Updet, Upfeats, Upiso
from django.db import connection
import subprocess
import datetime
from Bio import SwissProt, SeqIO

path  = 'data/protein/'

files = [ 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping_selected.tab.gz',
          'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/MOUSE_10090_idmapping_selected.tab.gz',
          'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/RAT_10116_idmapping_selected.tab.gz',          
          path + 'hs_uniprot.gz',
          path + 'mm_uniprot.gz',
          path + 'rn_uniprot.gz',
          path + 'uniprot_latest',
          'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_human.dat.gz',
          'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_rodents.dat.gz',
          'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_trembl_human.dat.gz',
          'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_trembl_rodents.dat.gz',
          'uniprot_sprot_human.dat',
          'uniprot_sprot_rodents.dat',
          'uniprot_trembl_human.dat',
          'uniprot_trembl_rodents.dat',
          'uniprot_sprot.dat',
          'uniprot_features.dat',
          'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz', 
          'uniprot_isos.dat',
          'uniprot_isoforms.dat']

xrefs = ['GeneID', 'Refseq', 'MGI', 'HGNC']
xdoms = ['PROSITE', 'InterPro', 'CDD', 'SMART', 'Pfam', ]

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
        print( 'download files from uniprot ftp site' )
        subprocess.call([ 'wget', '-q', files[0],  '-O', files[3] ])
        subprocess.call([ 'wget', '-q', files[1],  '-O', files[4] ])
        subprocess.call([ 'wget', '-q', files[2],  '-O', files[5] ])        
        subprocess.call([ 'wget', '-q', files[7],  '-O', path+files[11]+'.gz' ])
        subprocess.call([ 'wget', '-q', files[8],  '-O', path+files[12]+'.gz' ])
        subprocess.call([ 'wget', '-q', files[9],  '-O', path+files[13]+'.gz' ])
        subprocess.call([ 'wget', '-q', files[10], '-O', path+files[14]+'.gz' ])
        subprocess.call([ 'wget', '-q', files[17], '-O', path+files[18]+'.gz' ])
        for i in [11,12,13,14,18]:
            print('gunzip: ' + path + files[i] + '.gz')
            gunzip( path+files[i]+'.gz', path, files[i] )

                          
    def _parse_xref_files( self ):

        with open( files[6], 'wt' ) as outf:

            #print( 'parse downloaded data files.' )
            maxeid    = 0
            maxrsid   = 0
            maxomim   = 0
            maxpmid   = 0
            maxensid  = 0
            maxenspid = 0            

            print( 'xref files...' )
            for i in range(3,6,1):
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


    def _parse_flat_files( self ):
    
        print( 'uniprot flat files...' )
        with open( path + files[15], 'wt' ) as outf:

            for j in [11,12,13,14]:
                print( files[j] + '...' )
                with open(path + files[j], 'rt') as handle:
                    for record in SwissProt.parse(handle):
                        if record.taxonomy_id[0] in ['9606', '10090', '10116']:
                            accs  = record.accessions
                            acc   = accs.pop(0)
                            rev   = record.data_class
                            gname = re.sub(r'.*Name=([^;{]+)[{;].*', r'\1', record.gene_name).strip()
                            uid   = record.entry_name
                            taxid = record.taxonomy_id[0]
                            seq   = record.sequence
                            sinfo = str(record.seqinfo[0])
                            srcdb = 'sp'
                            if re.search(r'trembl', files[j]):
                                srcdb = 'tr'
                            rname = ''
                            fname = ''
                            sname = ''
                            flags = ''
                            if 'RecName' in record.description:
                                rname = re.sub(r'.*RecName: *Full=([^;{]+)[{;].*', r'\1', record.description, re.IGNORECASE).strip()
                            elif 'SubName' in record.description:
                                rname = re.sub(r'.*SubName: *Full=([^;{]+) *[;{].*', r'\1', record.description, re.IGNORECASE).strip()
                            if 'AltName' in record.description:
                                if re.search(r'AltName:[^:]*Full=', record.description, re.IGNORECASE): 
                                    fname = re.sub(r'.*AltName:[^:]*Full=([^;{]+)[{;].*', r'\1', record.description, re.IGNORECASE).strip()
                                if re.search(r'AltName:[^:]*Short=', record.description, re.IGNORECASE): 
                                    sname = re.sub(r'.*AltName:[^:]*Short=([^;{]+)[{;].*', r'\1', record.description, re.IGNORECASE).strip()
                            if 'Flags:' in record.description:
                                flags = re.sub(r'.*Flags: *([^;]+);.*', r'\1', record.description, re.IGNORECASE).strip()
                            refs  = list()
                            eids  = list()
                            mgis  = list()
                            hgnc  = list()
                            dids  = list()
                            dnms  = list()
                            ddbs  = list()
                            for i in range(0, len(record.cross_references)):
                                if record.cross_references[i][0] == 'GeneID':
                                    eids.append(record.cross_references[i][1])
                                if record.cross_references[i][0] == 'RefSeq':
                                    refs.append(re.sub(r'\.\d+$', r'', record.cross_references[i][1]))
                                if record.cross_references[i][0] == 'MGI':
                                    mgis.append(record.cross_references[i][1])
                                if record.cross_references[i][0] == 'HGNC':
                                    hgnc.append(record.cross_references[i][1])
                                if record.cross_references[i][0] in xdoms:
                                    dids.append(record.cross_references[i][1])
                                    ddbs.append(record.cross_references[i][0])
                                    dnms.append(record.cross_references[i][2])
                            outf.write( '\t'.join([ acc, uid, srcdb, taxid, rev, gname, rname, fname, sname, flags, '|'.join(accs), '|'.join(eids), '|'.join(refs), '|'.join(hgnc), '|'.join(mgis), '|'.join(ddbs), '|'.join(dids), '|'.join(dnms), sinfo, seq ]) + '\n' )          

    def _parse_features( self ):
    
        print( 'uniprot flat files, to get features...' )
        with open( path + files[16], 'wt' ) as outf:

            for j in [11,12,13,14]:
                print( files[j] + '...' )
                with open(path + files[j], 'rt') as handle:
                    for record in SwissProt.parse(handle):
                        if record.taxonomy_id[0] in ['9606', '10090', '10116']:
                            accs  = record.accessions
                            acc   = accs.pop(0)
                            feats = record.features
                            for f in feats:
                                f = list(f)
                                f.insert(3, '')
                                if re.search(r'^[^\.]+\.\s*$', f[4]):
                                    m = re.match(r'^(.+)\.\s*$', f[4])
                                    if m:
                                        f[3] = m.group(1)
                                        f[4] = ''
                                elif re.search(r'.+\.\s+\{', f[4]):
                                    m = re.match(r'^(.+)\.\s*\{(.+)\}\.$', f[4])
                                    if m:
                                        f[3] = m.group(1)
                                        f[4] = m.group(2)
                                elif re.search(r'.+\.\s+\/', f[4]):
                                    m = re.match(r'^(.+)\.\s*\/(.+)\.$', f[4])
                                    if m:
                                        f[3] = m.group(1)
                                        f[4] = m.group(2)                                
                                else :
                                    f[4] = re.sub(r'[\{\}\.\/]', '', f[4]) 
                                #print(f)
                                outf.write( acc + "\t" + '\t'.join(map(str, f)) + '\n')

    def _parse_isoseqs( self ):     

        print( 'uniprot isoform fasta file...' )
        
        fasta_sequences = SeqIO.parse(open(path+files[18]),'fasta')
        with open( path + files[19], 'wt' ) as outf:
            for fasta in fasta_sequences:
                upids, upseq, upname = fasta.id, str(fasta.seq), fasta.description
                if re.search('.+(_HUMAN|_MOUSE|_RAT)', upids):
                    isoid = re.sub(r'^..\|(.+)\|.+', r'\1', upids)
                    upacc = re.sub(r'^(.+)-\d+', r'\1', isoid)
                    upid  = re.sub(r'^.+\|([^\|]+)$', r'\1', upids)
                    upname = re.sub(upids + ' ', r'', upname)
                    upname = re.sub(r'\|+', r'', upname)
                    outf.write('\t'.join([upacc, upid, isoid, upname, upseq]) + '\n')
                    

                            
    def _load_dbtable( self ):

        print( 'load data into uniprot table' )
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
                       , [ files[6] ] )
            #c.execute( 'ALTER TABLE uniprot ADD INDEX upacc_i (upacc );' )
            #c.execute( 'ALTER TABLE uniprot ADD INDEX upid_i (upid );' )
            #c.execute( 'ALTER TABLE uniprot ADD INDEX eid_i (eid );' )                        
        print( 'load data into updet table' )
        Updet.objects.all().delete()
        with connection.cursor() as c:
            c.execute( "LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.updet FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '\"' " + 
                       '(upacc, upid, srcdb, taxid, status, gname, recname, fullname, shortname, flags, upaccs, eid, refseqid, hgncid, mgid, domaindb, domainid, domainname, seqinfo, seq)', [ path + files[15] ] )
        print( 'load data into upfeats table' )
        Upfeats.objects.all().delete()
        with connection.cursor() as c:
            c.execute( "LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.upfeats FIELDS TERMINATED BY '\t' " + 
                       '(upacc, ftype, fstart, fstop, feature, source, extid)', [ path + files[16] ] )
        print( 'load data into upiso table' )
        Upiso.objects.all().delete()
        with connection.cursor() as c:
            c.execute( "LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE tcga.upiso FIELDS TERMINATED BY '\t' " + 
                       '(upacc, upid, isoid, descr, seq)', [ path + files[19] ] )
            
        
    def handle(self, *args, **options):
        print( '\n\n\n\n############################ ' + 'update uniprot data on ' + str(datetime.date.today()))
        if options[ 'reload' ]:
            print( 'reload data into database.' )
            self._load_dbtable()
        elif options[ 'reparse' ]:
            print( 'reparse and load data.' )
            self._parse_isoseqs()
            self._parse_xref_files()
            self._parse_flat_files()
            self._parse_features()
            self._load_dbtable()
        else:
            print( 'no argument - do whole process.' )
            self._download_from_uniprot()
            self._parse_xref_files()
            self._parse_flat_files()
            self._parse_features()
            self._parse_isoseqs()            
            self._load_dbtable()
