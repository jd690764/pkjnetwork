import os
import re
import pickle
import pandas

from django.core.management.base import BaseCommand
from django.db import connection
from network.models import Refseq, Entrez

from lib.config import filesDict



class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _update_dup( self ):

        entrez  = Entrez.objects.values( 'eid', 'symbol', 'taxid', 'swissprot', 'trembl' )
        edict   = {}
        spdict1 = {}
        spdict2 = {}
        spdict3 = {}
        trdict1 = {}
        trdict2 = {}
        trdict3 = {}        
        for dic in entrez:
            edict[dic[ 'eid' ]] = ( dic[ 'eid' ], dic[ 'symbol' ], dic[ 'taxid' ] )
            if dic[ 'swissprot' ]:
                sp = re.sub(r'^(.+)\.?\d*$', r'\1', dic[ 'swissprot' ])
                spdict1[ sp ] = dic[ 'eid' ]
                spdict2[ sp ] = dic[ 'symbol' ]
                spdict3[ sp ] = dic[ 'taxid' ]
            if dic[ 'trembl' ]:
                trdict1[dic[ 'trembl' ]] = dic[ 'eid' ]
                trdict2[dic[ 'trembl' ]] = dic[ 'symbol' ]
                trdict3[dic[ 'trembl' ]] = dic[ 'taxid' ] 

        refseq  = Refseq.objects.values( 'prot_acc', 'eid' )
        rsdict1 = {}
        rsdict2 = {}
        rsdict3 = {}
        for dic in refseq:
            rsdict1[dic[ 'prot_acc' ]] = edict[ dic[ 'eid' ]][0]
            rsdict2[dic[ 'prot_acc' ]] = edict[ dic[ 'eid' ]][1]
            rsdict3[dic[ 'prot_acc' ]] = edict[ dic[ 'eid' ]][2]
            
        dup = pickle.load( open( filesDict['dup'], 'rb' ))
        dup_df = pandas.DataFrame.from_dict(dup).T
        # create column from row names
        dup_df.index.name = 'descr'
        dup_df.reset_index(inplace = True)
        # name the other columns
        dup_df.columns = ['descr', 'eid', 'symbol', 'taxid', ]
        # parse out swissprot and ncbi ids from the description field - save them into column p
        dup_df['p'] = [re.sub(r'^.*(ref|REF)\|([A-Z]P_\d+)\.?\d*\|?.*$', r'\2', z) for z in [
            re.sub(r'^.*(sp|SP|tr|TR)\|([^\|]+)\|.*$', r'\2', str) for str in dup_df['descr']
        ]]

        #print( dup_df.loc[dup_df['p'] == 'q5sy55' ])
        dup_df['neid']    = [ rsdict1.get(z, z) for z in [ trdict1.get(y, y) for y in [ spdict1.get(x, x)  for x in [ w.upper() for w in dup_df['p']]]]]
        dup_df['nsymbol'] = [ rsdict2.get(z, z) for z in [ trdict2.get(y, y) for y in [ spdict2.get(x, x)  for x in [ w.upper() for w in dup_df['p']]]]]
        dup_df['ntaxid']  = [ rsdict3.get(z, z) for z in [ trdict3.get(y, y) for y in [ spdict3.get(x, x)  for x in [ w.upper() for w in dup_df['p']]]]]
        #print( dup_df.loc[dup_df['p'] == 'q5sy55' ])
        # if we could not find the entrez id, reuse the old one
        dup_df['neid']    = dup_df.apply(lambda x : x['eid'] if x['neid'] == x['p'].upper() else x["neid"], axis=1)
        dup_df['nsymbol'] = dup_df.apply(lambda x : x['symbol'] if x['nsymbol'] == x['p'].upper() else x["nsymbol"], axis=1)
        dup_df['ntaxid']  = dup_df.apply(lambda x : x['taxid'] if x['ntaxid'] == x['p'].upper() else x["ntaxid"], axis=1)

        # handle a dataframe conversion artefact
        dup_df['nsymbol'] = dup_df.apply(lambda x : None if x['symbol'] == x['eid'] else x["nsymbol"], axis=1)
        dup_df['ntaxid']  = dup_df.apply(lambda x : None if x['taxid'] == x['eid'] else x["ntaxid"], axis=1)
        #print( dup_df.loc[dup_df['p'] == 'q5sy55' ])
        result = {}
        for i in range(len(dup_df)):
            if dup_df.ix[i, 'nsymbol'] is None and dup_df.ix[i, 'ntaxid'] is None:
                result[dup_df.ix[i, 'descr']] = str(dup_df.ix[i, 'neid'])
            else:
                result[dup_df.ix[i, 'descr']] = (str(dup_df.ix[i, 'neid']), dup_df.ix[i, 'nsymbol'], str(dup_df.ix[i, 'ntaxid']))

        # rename previous file
        os.rename( filesDict['dup'], filesDict['dup']+ '.old')
        pickle.dump(result, open( filesDict['dup'], 'wb'))
        
    def handle(self, *args, **options):
        self._update_dup()

