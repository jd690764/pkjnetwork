from django.contrib import admin
from lib.forms import DropdownFilter
import re
import datetime
#from django.core import management
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline
from django.http import HttpResponseRedirect

# Register your models here.

from .models import Hgnc, Sample, Preprocess, Experiment, Psample, Fraction, Frms, Mspec, Dproc, Preproc, ExperimentEdit, PsampleProxy, FractionProxy, MspecProxy, DprocProxy, PreprocProxy, FrmsProxy, SummaryView


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

def map_fraction_to_ms( modeladmin, require, queryset ):
    for object in queryset:
        expid = object.id
        fractions = Fraction.objects.filter(expid_id = expid).order_by('id')
        ms = Mspec.objects.filter(expid_id = expid).order_by('id')
        min_elements = min(len(fractions), len(ms))
        for i in range(min_elements):
            Frms.objects.create(expid_id = expid, frid_id = fractions[i].id, msid_id = ms[i].id, name = fractions[i].name)

    return HttpResponseRedirect("admin/network/experiment/?q=%s" % (queryset[0].id))

map_fraction_to_ms.short_description = 'Link Fractions to MS spectra for Experiment(s)'

        
@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'uid', 'label', 'cell_line', 'cond', 'variant', 'tag', 'tag_length', 'facility', 'bait_symbol', 'eid', 'rawfile',
                    'bgfile','raw_folder', 'lab', 'exptype', 'note', 'ff_folder', 'box_folder', 'date_back', 'taxid', 'discard', 'display')
    list_filter = (('lab', DropdownFilter), ('cell_line', DropdownFilter), ('taxid', DropdownFilter))

    search_fields = ['uid', 'label', 'cond', 'variant', 'tag', 'facility', 'bait_symbol', 'exptype', 'note']

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

#admin.site.register(Frms)
        
# @admin.register(ProtSample)
# class ProtSampleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'uid', 'name', 'cell_line', 'treatment', 'variant', 'genotype', 'tag', 'tag_length', 'bait_symbol', 'eid',
#                     'lab', 'exptype', 'note', 'experimenter', 'date', 'taxid', 'discard', 'fractions')
#     list_filter = (('lab', DropdownFilter), ('exptype', DropdownFilter), ('bait_symbol', DropdownFilter), ('uid', DropdownFilter))

#     search_fields = ['uid', 'name']
    
#     actions = [duplicate_record]

#     def formfield_for_dbfield(self, db_field, **kwargs):
#         field =  super(ProtSampleAdmin, self).formfield_for_dbfield(db_field, **kwargs)
#         if db_field.name == 'taxid':
#             field.initial = '9606'
#         elif db_field.name == 'uid':
#             x = Sample.objects.filter(uid__contains = 'PJX').values('uid')
#             field.initial = 'PJX' + str(max([int(re.sub(r'PJX', r'', id['uid'])) for id in x]) + 1)
#         elif db_field.name == 'exptype':
#             field.initial = 'apms'
#         elif db_field.name == 'lab':
#             field.initial = 'jackson'
#         elif db_field.name == 'discard':
#             field.initial = 'False'
#         elif db_field.name == 'tag_length':
#             field.initial = 0
#         elif db_field.name == 'date':
#             field.initial  = datetime.datetime.today().strftime('%Y-%m-%d')
#         elif db_field.name == 'fractions':
#             field.initial = 8
#         elif db_field.name == 'fractions':
#             field.initial = 'NANCIE'            
#         return field
        
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
    

class PsampleInline(NestedStackedInline):
    model = Psample
    extra = 0

class FractionInline(NestedStackedInline):
    model = Fraction
    extra = 0

class MspecInline(NestedStackedInline):
    model = Mspec
    extra = 0

class DprocInline(NestedStackedInline):
    model = Dproc
    extra = 0

class PreprocInline(NestedStackedInline):
    model = Preproc
    extra = 0

class PsampleProxyInline(NestedStackedInline):
    model = PsampleProxy
    extra = 0

class FractionProxyInline(NestedStackedInline):
    model = FractionProxy
    extra = 0

class FrmsProxyInline(NestedStackedInline):
    model = FrmsProxy
    extra = 0

class MspecProxyInline(NestedStackedInline):
    model = MspecProxy
    extra = 0

class DprocProxyInline(NestedStackedInline):
    model = DprocProxy
    extra = 0

class PreprocProxyInline(NestedStackedInline):
    model = PreprocProxy
    extra = 0

#@admin.register(Psample)
#class PsampleAdmin(NestedModelAdmin):
#    list_display = ('id', 'name', 'bait_symbol', 'bait_eid', 'bait_variant', 'cell_line', 'genotype', 'treatment', 'tag', 'tag_length',
#                    'taxid', 'note', 'date', 'fractions')
#    list_filter = (('cell_line', DropdownFilter), ('bait_symbol', DropdownFilter))

#    search_fields = ['name', 'cell_line', 'treatment', 'bait_symbol']

#    actions = [duplicate_record]

#    inlines = [
#        FractionInline
#    ]    


#    def formfield_for_dbfield(self, db_field, **kwargs):
#        field =  super(PsampleAdmin, self).formfield_for_dbfield(db_field, **kwargs)
#        if db_field.name == 'taxid':
#            field.initial = '9606'
#        elif db_field.name == 'tag_length':
#            field.initial = 0
#        elif db_field.name == 'date':
#            field.initial  = datetime.datetime.today().strftime('%Y-%m-%d')
#        elif db_field.name == 'fractions':
#            field.initial = 8

#        return field

@admin.register(SummaryView)
class SummaryViewAdmin(admin.ModelAdmin):

    list_display = ('sid', 'dpid', 'ppid', 'uid', 'name', 'special', 'experimenter', 'lab', 'bait', 'eid', 'variant',
                    'cell_line', 'treatment', 'tag', 'tag_length', 'taxid', 'facility', 'machine', 'software',
                    'rawfile', 'bgfile', 'ff_folder', 'date_back', 'discard', 'display')
    search_fields = ['name', 'bait', 'variant', 'cell_line', 'lab', 'treatment', 'tag',
                     'facility', 'machine', 'uid', 'special', 'experimenter']

@admin.register(Psample)
class PsampleAdmin(NestedModelAdmin):
    list_display = ('id', 'name', 'bait_symbol', 'bait_eid', 'bait_variant', 'cell_line', 'genotype', 'treatment', 'tag',
                    'tag_length', 'taxid', 'note', 'date', 'fractions')
    list_filter = (('taxid', DropdownFilter), ('cell_line', DropdownFilter))
    
    search_fields = ['name', 'bait_symbol', 'treatment', 'note']

    inlines = [FractionInline]
    actions = [duplicate_record]

@admin.register(Fraction)
class FractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'psid', 'expid', 'name', 'digest', 'method', 'deriv')
    search_fields = ['name', 'digest', 'method', 'deriv']
    actions = [duplicate_record]
    
@admin.register(Mspec)
class MspecAdmin(NestedModelAdmin):
    list_display = ('id', 'expid', 'name', 'facility', 'machine', 'gradient', 'method', 'rundate', 'rawfolder')
    search_fields = ['name', 'gradient', 'method', 'machine']

    inlines = [DprocInline]
    actions = [duplicate_record]    

@admin.register(Dproc)
class DprocAdmin(NestedModelAdmin):
    list_display = ('id', 'msid', 'expid', 'name', 'software', 'paramfile', 'outfolder', 'rawfile', 'bgfile', 'ff_folder', 'date_back')
    search_fields = ['name']
    inlines  = [PreprocInline]
    actions = [duplicate_record]    

@admin.register(Preproc)
class PreprocAdmin(admin.ModelAdmin):
    list_display = ('id', 'dpid', 'expid', 'special', 'parser', 'comment', 'display')
    search_fields = ['special', 'parser', 'comment', 'display']
    actions = [duplicate_record]

@admin.register(Experiment)
class ExperimentAdmin(NestedModelAdmin):
    list_display = ('id', 'uid', 'name', 'exptype', 'experimenter', 'lab')
    list_filter = (('exptype', DropdownFilter), ('lab', DropdownFilter))

    search_fields = ['name', 'experimenter', 'uid']

    actions = [duplicate_record]

    inlines = [
        PsampleInline, MspecInline
    ]    


    def formfield_for_dbfield(self, db_field, **kwargs):
        field =  super(ExperimentAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'uid':
            x = Experiment.objects.filter(uid__contains = 'PJX').values('uid')
            field.initial = 'PJX' + str(max([int(re.sub(r'PJX', r'', id['uid'])) for id in x]) + 1)
        elif db_field.name == 'exptype':
            field.initial = 'apms'
        elif db_field.name == 'lab':
            field.initial = 'jackson'
        elif db_field.name == 'discard':
            field.initial = 'False'
        elif db_field.name == 'experimenter':
            field.initial = 'Nancie'            
        return field

@admin.register(ExperimentEdit)
class ExperimentEditAdmin(NestedModelAdmin):
    list_display = ('id', 'uid', 'name', 'exptype', 'experimenter', 'lab')
    list_filter = (('exptype', DropdownFilter), ('lab', DropdownFilter))

    search_fields = ['name', 'experimenter', 'uid']

    actions = [duplicate_record, map_fraction_to_ms]

    inlines = [
        PsampleProxyInline, FractionProxyInline, FrmsProxyInline, MspecProxyInline, DprocProxyInline, PreprocProxyInline
    ]    


