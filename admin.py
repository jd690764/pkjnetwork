from django.contrib import admin
from lib.forms import DropdownFilter

# Register your models here.

from .models import Hgnc, Sample

class HgncAdmin(admin.ModelAdmin):
    list_display = ('hgnc_id', 'symbol', 'hgnc_name', 'entrez_id')

admin.site.register(Hgnc, HgncAdmin)    
    
@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'uid', 'label', 'cell_line', 'condition', 'variant', 'tag', 'tag_length', 'facility', 'bait_symbol', 'eid', 'rawfile',
                    'bgfile','mrmsfile', 'lab', 'exptype', 'note', 'ff_folder', 'box_folder', 'date_back', 'taxid')
    list_filter = (('lab', DropdownFilter), ('facility', DropdownFilter), ('bait_symbol', DropdownFilter), ('uid', DropdownFilter))
    

