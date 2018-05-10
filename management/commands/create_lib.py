from django.core.management.base import BaseCommand

from network.models import Ncbiprots, Updet, Uniprot
from django.db import connection
import pandas as pd
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

# script to create search library for data proccessing by Byonic.
# the libraris are by organism and the entries are sorted
# as follows:
#     - have soupporting evidence in uniprot
#     - length of protein (high to low)
#     - NR first (XR affer)
#     - sp first, tr later - for corresponding uniprot entry

outdir = 'data/protein/'

sql = """select refseq, upacc, min(srcdb) srcdb
from (
        select
          distinct
          SUBSTRING_INDEX(SUBSTRING_INDEX(x.refseqid, ';', numbers.n), ';', -1) refseq,
          x.upacc,
          x.srcdb
        from
          numbers inner join (
          select p.upacc, p.refseqid, d.srcdb
                from uniprot p
                left join updet d on p.upacc = d.upacc
          ) x

          on CHAR_LENGTH(x.refseqid)
             -CHAR_LENGTH(REPLACE(x.refseqid, ';', ''))>=numbers.n-1
        order by 1,3,2
) y
group by refseq"""

class Command(BaseCommand):

    args = ''
    help = 'our help string comes here'
    
    def create_search_lib( self ):

        # retrieve refseq to uniprot map
        with connection.cursor() as cursor:
            cursor.execute( sql )
            ds = cursor.fetchall()

        ds = pd.DataFrame(list(ds), columns = ['rsid', 'upid', 'src'])

        # get refseq seqs and attributes
        rs = pd.DataFrame(list([(v['acc'], v['taxid'], v['protname'], v['eid'], v['symbol'], v['len'], v['seq'].upper())
                                for v in Ncbiprots.objects.values('acc', 'taxid', 'protname', 'eid', 'symbol', 'len', 'seq')]),
                          columns = ['acc', 'taxid', 'protname', 'eid', 'symbol', 'len', 'seq']
        )


        all = pd.merge(rs, ds, how = 'left', left_on = 'acc', right_on = 'rsid')

        # sort sequences by ...
        all = all.sort_values(by = ['taxid', 'src', 'len', 'acc', 'src'],
                              ascending = [True, True, False, True, True])

        org = 'human'

        # create fasta files
        for tid in [9606, 10090]:
            fasta = []
            if tid == 10090:
                org = 'mouse'
            for row in all.iterrows():
                index, data = row
                data = data.tolist()
                if data.pop(1) == tid:
                    data.pop(6)
                    seq = Seq(data.pop(5))
                    record = SeqRecord(seq)
                    record.id = data[0]
                    record.name = data.pop(0)
                    record.description = ' '.join([str(x) for x in data])
                    fasta.append(record)

            SeqIO.write(fasta, outdir + org + "._refseq.fasta", "fasta")


    def handle(self, *args, **options):
        self.create_search_lib()
