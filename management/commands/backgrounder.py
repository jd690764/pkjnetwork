from django.core.management.base import BaseCommand
from django.db import connection

from network.models import Preprocess, Sample

import lib.interactors as I
import lib.MSpreprocess as ms
from lib.markutils import *
from lib import config as cf
import pandas as pd
import subprocess as sp
import os

mrmspath      = cf.mrmsfilesPath
rawpath       = cf.rawfilesPath
ipath         = cf.ifilesPath
bgpath        = cf.bgfilesPath

pepDict       = { '9606': 'RPHs', '10090': 'RPMm' }

class Command(BaseCommand):
    #args = '<foo bar ...>'
    help = 'Preprocess rawfiles to ifiles.'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--byid',
            nargs   = '+',
            type    = int,
            #action  = 'store_true',
            #dest    = 'buid',
            #default = False,
            help    = 'Preprocess data from database by id. xxx --byid 1234 324 ...',
        )
        #parser.add_argument(
        #    '--byfile',
        #    action  = 'store_true',
        #    dest    = 'byfile',
        #    default = False,
        #    help    = 'Preprocess data from backgrounder.tsv file',
        #)

    def _process_byid( self, uid ):

        row     = Preprocess.objects.get( pk = uid )
        baitsym = b4us(row.bait_symbol_eid)
        sample  = Sample.objects.get( pk = int(row.sampleid) )
        self._process_dataset( row.rawfile, row.parser.upper(), baitsym, str(row.taxid), row.special, row.bgfile, row.mrmsfile, sample.id )        
    
    def _process_byfile( self ):

        instruction_f = open( cf.bgerfilePath )        
        for line in instruction_f : 
            if line[0] == '#' : 
                continue 

            linel           = line.rstrip().lstrip().split('\t')
            infilename      = linel[0] 
            baitsym         = b4us(linel[1]) 
            org             = linel[2]
            special         = linel[3]
            parser          = linel[4] 

            if len(linel) >= 6:
                bgfilename  = linel[5]
            else :
                bgfilename  = ''

            if len(linel) == 7:
                mrmsfile    = linel[6]
            else :
                mrmsfile    = ''
                
            self._process_dataset( infilename, parser.upper(), baitsym, str(org), special, bgfilename, mrmsfile, -1 )


    def _process_dataset( self, infilename, parser, baitsym, org, special, bgfilename, mrmsfile, sid ):

        if special and special[0] == '*' : 
            outfname_pfx   =    special[1:]
        elif special : 
            outfname_pfx   =    baitsym+'_'+str(org)+'_'+special+'_'
        else : 
            outfname_pfx   =    baitsym+'_'+str(org)+'_' 
            
        outfname = ipath + outfname_pfx + date6() + '.i'

        sys.stdout.write(outfname+'\n') 

        if not mrmsfile == None and os.path.isfile( mrmspath + mrmsfile ):
            infile = open( mrmspath + mrmsfile )
        elif not infilename == None and 'mrms' in infilename :
            infile = open( mrmspath + infilename ) 
        elif 'xml' in infilename :
            infile = open( rawpath + infilename, 'rb' )
        elif '.xlsx' in infilename and parser == 'SUMS':
            mrmsfile = mrmsfile if mrmsfile else re.sub( r'^(.+)\.xlsx', r'\1', infilename ) + '.mrms'
            if not os.path.isfile( mrmspath + mrmsfile ):
                exfile   = pd.ExcelFile( rawpath + infilename )
                if 'GLOBAL' in exfile.sheet_names:
                    sheet = 'GLOBAL'
                elif 'Global Percentile' in exfile.sheet_names:
                    sheet = 'Global Percentile'
                elif 'tableformat.csv' in exfile.sheet_names:
                    sheet = 'tableformat.csv'
                    
                exptdata = exfile.parse( sheet )
                #exptdata = pd.read_excel( rawpath + infilename, sheetname = "Global Percentile" )
                exptdata.to_csv( mrmspath + mrmsfile, sep = "\t", na_rep = 'NaN', index = False )
            infile = open( mrmspath + mrmsfile )
        elif '.xls' in infilename and parser == 'LANEEXCEL':
            mrmsfile = mrmsfile if mrmsfile else re.sub( '^(.+)\.xlsx', '\1', infilename ) + '.mrms'
            if not os.path.isfile( mrmspath + mrmsfile ):
                exptdata = pd.read_excel( rawpath + infilename, sheetname = "PeptideCountHeatMap" )
                exptdata.to_csv( mrmspath + mrmsfile, sep = "\t", na_rep = 'NaN', index = False )
            infile = open( mrmspath + mrmsfile )
        else : 
            raise TypeError

        # get coverage data file
        covfile = None
        if sid > 0:
            sample  = Sample.objects.get( pk = sid )
            if sample.ff_folder == None or sample.ff_folder == '':
                print( 'no ff_folder for sampleid=' + str(sid) ) 
            else:
                print(os.path.join(cf.ptmsPath, sample.ff_folder, sample.ff_folder + '_cov_summary.tsv'))
                if os.path.isfile(os.path.join(cf.ptmsPath, sample.ff_folder, sample.ff_folder + '_cov_summary.tsv')):
                    covfile = os.path.join(cf.ptmsPath, sample.ff_folder, sample.ff_folder + '_cov_summary.tsv')
                else:
                    # if this file dosn't exist, we need to run the modifs.R script now
                    sp.call(['Rscript', '/usr/local/share/R/modifs.R', '-u', str(sid)])
                    if os.path.isfile(os.path.join(cf.ptmsPath, sample.ff_folder, sample.ff_folder + '_cov_summary.tsv')):
                        covfile = os.path.join(cf.ptmsPath, sample.ff_folder, sample.ff_folder + '_cov_summary.tsv')

        print( 'infile=' + str(infilename) )
        print( 'baitsym=' + str(baitsym) )
        print( 'org=' + str(org) )
        print( 'special=' + str(special) )
        print( 'bgfile=' + str(bgfilename) )
        print( 'mrmsfile=' + str(mrmsfile) )
        print( 'covfile=' + str(covfile) )
        
        dataset = ms.MSdata( outfname_pfx + date6() )

        if parser == 'SUMS' :
            dataset.parseSUMS(infile) 
        elif parser == 'LANE' :
            dataset.parseLane(infile)
        elif parser == 'LANEEXCEL':
            dataset.parseLaneExcel(infile)
        elif parser == 'XML'  :
            dataset.parseXML(infile) 
        else : 
            raise TypeError 

        dataset.syncToEntrez( bestpepdb = pepDict[ org ], debug = True )
        if bgfilename and bgfilename != '': 
            dataset.set_background( bgpath + bgfilename, bestpepdb = pepDict[ org ] ) 

        dataset.setBait(baitsym)
        dataset.score()
        # if there are older version of this file move them into a separate folder
        prev_file = [f for f in os.listdir(ipath) if re.search(outfname_pfx + '\d+\.i$', f)]
        for pf in prev_file:
            sp.call(['mv', ipath + pf, ipath + 'old/' + pf])
        dataset.save(outfname, covfile = covfile)

    def handle(self, *args, **options):
        print( options )
        #if options[ 'byfile' ]:
        #    print( 'Preprocess from backgrounder.tsv file.' )
        #    self._process_byfile()
        #elif options[ 'byid' ]:
        for uid in options[ 'byid' ]:
            print( 'Preprocess from by id from database: ' + str(uid) )
            self._process_byid( uid )


    
