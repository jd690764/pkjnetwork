from django.contrib import admin
from lib.forms import DropdownFilter
import re
import datetime
#from django.core import management


# Register your models here.

from .models import Hgnc, Sample, Preprocess, ProtSample

class HgncAdmin(admin.ModelAdmin):
    list_display = ('hgnc_id', 'symbol', 'hgnc_name', 'entrez_id')

admin.site.register(Hgnc, HgncAdmin)    
def duplicate_record( modeladmin, request, queryset ):
    for object in queryset:
        object.id = None
        object.save()

duplicate_record.short_description = 'Duplicate selected record(s)'

def preprocess_from_sample( modeladmin, request, queryset ):
    for object in queryset:
        pp = Preprocess(rawfile = object.rawfile)
        pp.bait_symbol_eid = object.bait_symbol + '_' + str(object.eid)
        pp.taxid = object.taxid
        pp.parser = object.facility
        pp.bgfile = object.bgfile
        pp.mrmsfile = object.mrmsfile
        pp.pjx = object.uid
        pp.sampleid = object.id
        pp.save()

preprocess_from_sample.short_description = 'Create Preprocess record from Sample(s)'
        
@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'uid', 'label', 'cell_line', 'cond', 'variant', 'tag', 'tag_length', 'facility', 'bait_symbol', 'eid', 'rawfile',
                    'bgfile','raw_folder', 'lab', 'exptype', 'note', 'ff_folder', 'box_folder', 'date_back', 'taxid', 'discard', 'display')
    list_filter = (('lab', DropdownFilter), ('facility', DropdownFilter), ('bait_symbol', DropdownFilter), ('uid', DropdownFilter))

    actions = [duplicate_record, preprocess_from_sample]
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        field =  super(SampleAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'facility':
            field.initial = 'sums'
        elif db_field.name == 'taxid':
            field.initial = '9606'
        elif db_field.name == 'uid':
            x = Sample.objects.filter(uid__contains = 'PJX').values('uid')
            field.initial = 'PJX' + str(max([int(re.sub(r'PJX', r'', id['uid'])) for id in x]) + 1)
        elif db_field.name == 'type':
            field.initial = 'apms'
        elif db_field.name == 'lab':
            field.initial = 'jackson'
        elif db_field.name == 'discard':
            field.initial = 'False'
        elif db_field.name == 'tag_length':
            field.initial = 0
        elif db_field.name == 'date_back':
            field.initial  = datetime.datetime.today().strftime('%Y-%m-%d')
            
            
        return field
        
@admin.register(ProtSample)
class ProtSampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'uid', 'name', 'cell_line', 'treatment', 'variant', 'genotype', 'tag', 'tag_length', 'bait_symbol', 'eid',
                    'lab', 'exptype', 'note', 'experimenter', 'date', 'taxid', 'discard', 'fractions')
    list_filter = (('lab', DropdownFilter), ('exptype', DropdownFilter), ('bait_symbol', DropdownFilter), ('uid', DropdownFilter))

    actions = [duplicate_record]
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        field =  super(ProtSampleAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'taxid':
            field.initial = '9606'
        elif db_field.name == 'uid':
            x = Sample.objects.filter(uid__contains = 'PJX').values('uid')
            field.initial = 'PJX' + str(max([int(re.sub(r'PJX', r'', id['uid'])) for id in x]) + 1)
        elif db_field.name == 'exptype':
            field.initial = 'apms'
        elif db_field.name == 'lab':
            field.initial = 'jackson'
        elif db_field.name == 'discard':
            field.initial = 'False'
        elif db_field.name == 'tag_length':
            field.initial = 0
        elif db_field.name == 'date':
            field.initial  = datetime.datetime.today().strftime('%Y-%m-%d')
        elif db_field.name == 'fractions':
            field.initial = 8
        elif db_field.name == 'fractions':
            field.initial = 'NANCIE'            
        return field
        
@admin.register(Preprocess)
class PreprocessAdmin(admin.ModelAdmin):
    list_display = ('id', 'rawfile', 'bait_symbol_eid', 'taxid', 'special', 'parser', 
                    'bgfile','mrmsfile', 'comment', 'pjx', 'sampleid' )
    list_filter  = (('bait_symbol_eid', DropdownFilter), ('parser', DropdownFilter))

    actions = [duplicate_record]
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        field =  super(PreprocessAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'parser':
            field.initial = 'sums'
        elif db_field.name == 'taxid':
            field.initial = '9606'
        elif db_field.name == 'pjx':
            x = Preprocess.objects.filter(pjx__contains = 'PJX').values('pjx')
            field.initial = 'PJX' + str(max([int(re.sub(r'PJX', r'', id['pjx'])) for id in x]) + 1)
        return field
    
    #actions      = ['run_preprocess']

    
    #def run_preprocess( self, request, queryset):
    #    for obj in queryset:
    #        uid = obj.id
    #        management.call_command('backgrounder', u = uid)
            #res = subprocess.run( ['python3', 'manage.py', 'backgrounder', '--u', str(uid)], stdout = subprocess.PIPE, stderr = subprocess.PIPE )

            #if res.returncode == 0:
            #    self.message_user(request, "%s was successfully preprocessed." % uid)
            #else:
            #    self.message_user(request, "Problem during preprocessing: %s" % res.stderr)
                
    #run_preprocess.short_description = 'Run preprocessing for selected items.'
