#admin12345
from django.contrib import admin

# Register your models here.
from .models import Bom
from .models import BomDetails
from .models import Station
from .models import Routing
from .models import RoutingDetails
from .models import Product
from .models import WorkOrder
from .models import WorkOrderDetails
from .forms import StationModelForm
from .models import Performing
from .models import PerformingDetails
from .models import Family
from .models import Parameter
from .models import DocumentControls
from .models import DocumentLogs
from .models import DocumentRelated
from .models import Components
from .models import ComponentsTracking


class BomDetailsInline(admin.TabularInline):
    model = BomDetails
    extra = 1

class BomAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['model']
    list_display = ('name','model','rev','description')
    fieldsets = [
        (None,               {'fields': ['name','model','rev','description']}),
    ]
    inlines = [BomDetailsInline]

admin.site.register(Bom,BomAdmin)

class StationAdmin(admin.ModelAdmin):
    search_fields = ['station','family__name']
    list_filter = ['process','name','family__name','first_process','last_process','critical']
    list_display = ('station','name','family','process','first_process','last_process','description','critical','ordering')
    empty_value_display = ''
    fieldsets = [
        (None,               {'fields': ['station','name','family','process','first_process',
            'last_process','description','critical','ordering']}),
    ]

    #form = StationModelForm
    # search_fields = ['station']
    # list_filter = ['name']
    # list_display = ('station','name','description')
    # fieldsets = [
    #     (None,               {'fields': ['station','name','description']}),
    # ]
    # form = StationModelForm

admin.site.register(Station,StationAdmin)


#Routing
class RoutingDetailsInline(admin.TabularInline):
    model = RoutingDetails
    extra = 1

class RoutingAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['name']
    list_display = ('name','description')
    fieldsets = [
        (None,               {'fields': ['name','description']}),
    ]
    inlines = [RoutingDetailsInline]

admin.site.register(Routing,RoutingAdmin)

#Product
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['family','model','customer_model']
    list_display = ('name','description','model','rev','family','customer_model','customer_rev')
    fieldsets = [
        (None,               {'fields': ['name','description','model','rev','family','customer_model','customer_rev','bom']}),
    ]

admin.site.register(Product,ProductAdmin)

#WorkOrder
class WorkOrderDetailsInline(admin.TabularInline):
    model = WorkOrderDetails
    extra = 1

class WorkOrderAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['product__family','product','build_type']
    list_display = ('name','product','registered','inprocess','completed','shipped','build_type')
    fieldsets = [
        (None,               {'fields': ['name','description','product','qty','build_type']}),
    ]
    inlines = [WorkOrderDetailsInline]

admin.site.register(WorkOrder,WorkOrderAdmin)

class PerformingDetailsInline(admin.TabularInline):
    model = PerformingDetails
    extra = 1
    exclude = ['value','created_date','user']

class PerformingAdmin(admin.ModelAdmin):
    search_fields = ['sn_wo__sn']#sn_wo__sn
    list_filter = ['loop','sn_wo__status','result','station']#'sn_wo__workorder','sn_wo__workorder__product__name','sn_wo__status','station','result'
    list_display = ('get_sn','get_workorder','station','loop','tester','started_date','finished_date','result','dispose_code')
    fieldsets = [
        (None,               {'fields': ['sn_wo','station','loop','tester','result','dispose_code']}),
    ]
    inlines = [PerformingDetailsInline]

    def get_sn(self, obj):
        return obj.sn_wo.sn
    get_sn.short_description = 'Serial number'
    get_sn.admin_order_field = 'sn_wo__sn'

    def get_workorder(self, obj):
        return obj.sn_wo.workorder
    get_workorder.short_description = 'WorkOrder'
    get_workorder.admin_order_field = 'sn_wo__workorder'


    #inlines = [BomDetailsInline]
admin.site.register(Performing,PerformingAdmin)

class FamilyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['name','critical']
    list_display = ('name','description','critical','created_date','modified_date')
    fieldsets = [
        (None,               {'fields': ['name','description','critical']}),
    ]
    
admin.site.register(Family,FamilyAdmin)


class ParameterAdmin(admin.ModelAdmin):
    search_fields = ['name','group','description']
    list_filter = ['group','units','activated','critical']
    list_display = ('name','units','group','attribute','description','activated','created_date','modified_date',
        'critical','ordering')
    fieldsets = [
        (None,               {'fields': ['name','units','group','description','attribute','activated','critical','ordering']}),
    ]
    
admin.site.register(Parameter,ParameterAdmin)

class DocumentControlsLogInline(admin.TabularInline):
    model = DocumentLogs
    extra = 1
    #exclude = ['details','created_date','user']

class DocumentRelatedInline(admin.TabularInline):
    model = DocumentRelated
    extra = 1
    #exclude = ['details','created_date','user']

class DocumentControlsAdmin(admin.ModelAdmin):
    search_fields = ['doc_number','title','details']
    list_filter = ['doc_type','status']
    list_display = ('doc_number','doc_type','title','log_total','document_total',
        'received_date','initial_date','finished_date','bom_process','user','status')
    fieldsets = [
        (None,               
            {'fields': ['doc_number','doc_type','title','details','received_date','initial_date',
            'finished_date','bom_process','user','status']}),
    ]
    inlines = [DocumentControlsLogInline,DocumentRelatedInline]
    
admin.site.register(DocumentControls,DocumentControlsAdmin)

class ComponentsTrackingInline(admin.TabularInline):
    model = ComponentsTracking
    extra = 1
    
class ComponentsAdmin(admin.ModelAdmin):
    search_fields = ['part_id','part_no','mfg_name','mfg_partno','mfg_datecode','mfg_lotcode','rtno']
    list_filter = ['mfg_name']
    list_display = ('part_id','part_no','mfg_name','mfg_partno','mfg_datecode','mfg_lotcode','rtno')
    fieldsets = [
        (None,               {'fields': ['part_id','part_no','mfg_name','mfg_partno','mfg_datecode','mfg_lotcode','rtno']}),
    ]
    inlines = [ComponentsTrackingInline]
    
admin.site.register(Components,ComponentsAdmin)

