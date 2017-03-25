#admin12345
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.filters import RelatedOnlyFieldListFilter

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
from .models import Tester
from .models import TesterParameterLimit
from django.db.models import Q


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

def modify_spc_setting_parameter(self, request, queryset):
    firstItem=True
    for obj_station in queryset:
        if firstItem :
            obj_first_tester_param = obj_station.parameter_used.filter(spc_control=True)
            if obj_first_tester_param.filter(spc_control=True).count()==0:
                self.message_user(request, "First item ,there is no spc control parameter", level=messages.ERROR)
                return
        else:
            if obj_first_tester_param.count() < obj_station.parameter_used.filter(spc_control=True).count() :
                self.message_user(request, "First item ,spc control parameter less than another item", level=messages.ERROR)
                return
            print ('Before update :%s--%s--%s'%(obj_station.station,obj_station.family,obj_station.parameter_used.filter(spc_control=True).count()))
            
            obj_other_station_parm = obj_station.parameter_used.all()
            obj_other_station_parm.update(spc_control=False,spc_ordering=100,
                lower_spec_limit=None,upper_spec_limit=None)

            for i in obj_first_tester_param :
                # print ('%s--%s--%s--%s--%s' % (i.name,i.spc_control,i.spc_ordering,i.lower_spec_limit,i.upper_spec_limit))
                objX = obj_other_station_parm.get(name=i.name)
                objX.spc_control=True
                objX.spc_ordering=i.spc_ordering
                objX.lower_spec_limit=i.lower_spec_limit
                objX.upper_spec_limit=i.upper_spec_limit
                objX.save()

            print ('After update :%s--%s--%s'%(obj_station.station,obj_station.family,obj_station.parameter_used.filter(spc_control=True).count()))

        firstItem=False



        
    # parameter_used

    self.message_user(request, "Modify all setting parameter successfully")
modify_spc_setting_parameter.short_description = "Modify SPC parameter setting"


class StationAdmin(admin.ModelAdmin):
    search_fields = ['station','family__name']
    list_filter = ['process','family__name','first_process','last_process','critical','spc_control']
    list_display = ('station','name','family','process','first_process','last_process',
        'description','critical','ordering','spc_control','spc_ordering')
    empty_value_display = ''
    fieldsets = [
        (None,               {'fields': ['station','name','family','process','first_process',
            'last_process','description','critical','ordering','spc_control','spc_ordering']}),
    ]
    actions=[modify_spc_setting_parameter]

    

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
    list_display = ('name','description','model','rev','family','customer_model','customer_rev','group')
    fieldsets = [
        (None,               {'fields': ['name','description','model','rev','family','customer_model','customer_rev','group','bom']}),
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
    list_display = ('name','description','critical','spc_control','spc_ordering','created_date','modified_date')
    fieldsets = [
        (None,               {'fields': ['name','description','critical','spc_control','spc_ordering']}),
    ]
    
admin.site.register(Family,FamilyAdmin)


class ParameterAdmin(admin.ModelAdmin):
    search_fields = ['name','description']
    list_filter = ['critical','spc_control','station__family','station__station','group','units','activated']
    list_display = ('name','description','units','station','activated',
        'critical','ordering','spc_control','spc_ordering','lower_spec_limit','upper_spec_limit')
    fieldsets = [
        (None,               {'fields': ['name','units','group','station','description',
            'attribute','activated','critical','ordering','spc_control','spc_ordering','lower_spec_limit','upper_spec_limit']}),
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(ParameterAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['station'].queryset = Station.objects.filter(Q(spc_control=True) | Q(critical=True)).order_by('family','station')
        return form

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "station":
    #         kwargs["queryset"] = Station.objects.order_by('family','station')
    #     return super(ParameterAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
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


class TesterParameterLimitAdmin(admin.ModelAdmin):
    search_fields = ['tester','parameter']
    list_filter = [('tester__station',RelatedOnlyFieldListFilter)]
    list_display = ('tester','parameter','cl','lcl','ucl')
    fieldsets = [
        (None,               {'fields': ['tester','parameter','cl','lcl','ucl']}),
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super(TesterParameterLimitAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['parameter'].queryset = Parameter.objects.filter(spc_control=True)
        return form

    # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    #     field = super(TesterParameterLimitAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    #     if db_field.name == 'parameter':
    #         obj_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
    #         obj_tester = self.get_object(request, Tester)
    #         kwarg={"spc_control":True}
    #         if obj_tester :
    #             kwarg={"spc_control":True,"station":obj_tester.station}
    #         field.queryset = field.queryset.filter(**kwarg).order_by('spc_ordering')
    #     return field

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "tester__station":
    #         kwargs["queryset"] = Station.objects.order_by('family','station')
    #     return super(TesterAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
admin.site.register(TesterParameterLimit,TesterParameterLimitAdmin)



class TesterParameterLimitAdminInline(admin.TabularInline):
    model = TesterParameterLimit
    extra = 1
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(TesterParameterLimitAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['parameter'].queryset = Parameter.objects.filter(spc_control=True)
    #     return form
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(TesterParameterLimitAdminInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'parameter':
            obj_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
            obj_tester = self.get_object(request, Tester)
            kwarg={"spc_control":True}
            if obj_tester :
                kwarg={"spc_control":True,"station":obj_tester.station}
            field.queryset = field.queryset.filter(**kwarg).order_by('spc_ordering')
        return field

    def get_object(self, request, model):
        object_id = request.META['PATH_INFO'].strip('/').split('/')[-2]
        try:
            object_id = int(object_id)
        except ValueError:
            return None
        return model.objects.get(pk=object_id)



    # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    #     if db_field.name == 'parameter':
    #         kwargs = Parameter.objects.filter(spc_control=True)
    #     else:
    #         pass
    #     return super(TesterParameterLimitAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

def create_parameter_setting(self, request, queryset):
    for obj_tester_slot in queryset:
        if obj_tester_slot.limittester_list.all().count() >0 :
            self.message_user(request, "there is parameter exist.", level=messages.ERROR)
            return
        #get spc_control parameter
        obj_spc_param = obj_tester_slot.station.parameter_used.filter(spc_control=True).order_by('spc_ordering')
        print ('There are %s parameter(s)' % obj_spc_param.count())
        for i in obj_spc_param:
            ts,created = TesterParameterLimit.objects.get_or_create(tester=obj_tester_slot,
                        parameter=i,cl=None,lcl=None,ucl=None)

    self.message_user(request, "Create default parameter setting successfully")
create_parameter_setting.short_description = "Create default Parameter Setting"


def copy_setting_parameter(self, request, queryset):
    firstItem=True
    for obj_tester_slot in queryset:
        print (obj_tester_slot.limittester_list.count())
        # if firstItem :
        if firstItem :
            obj_first_test_slot = obj_tester_slot.limittester_list.all()
            if obj_first_test_slot.count()==0:
                self.message_user(request, "First item ,no setting details", level=messages.ERROR)
                return

            # print ('Total main setting : %s' % obj_first_test_slot.count() )
        else:
            # delete all setting
            # print ('Delete data of %s',obj_tester_slot)
            obj_tester_slot.limittester_list.all().delete()
            for i in obj_first_test_slot :
                print ('%s--%s--%s--%s'%(i.tester,i.parameter,i.ucl,i.lcl))
                # Must used parameter of thier Family
                if i.tester.station.family != obj_tester_slot.station.family :
                    print ('Difference Family')
                    # Get parameter
                    new_param=Parameter.objects.get(name=i.parameter.name,station=obj_tester_slot.station)
                    ts,created = TesterParameterLimit.objects.get_or_create(tester=obj_tester_slot,
                        parameter=new_param,cl=i.cl,lcl=i.lcl,ucl=i.ucl)
                else:
                    ts,created = TesterParameterLimit.objects.get_or_create(tester=obj_tester_slot,
                        parameter=i.parameter,cl=i.cl,lcl=i.lcl,ucl=i.ucl)
                if not created:
                    self.message_user(request, "Unable to create setting of %s" % obj_tester_slot, level=messages.ERROR)
            # return
            # for obj_setting in obj_tester_slot.limittester_list.all():
            #     print ('%s--%s--%s'%(obj_setting.parameter.name,obj_setting.ucl,obj_setting.lcl))
        firstItem=False
        # print (obj.limittester_list.count())
    #     obj.status='USED'
    #     obj.actived=True
    #     obj.save()
    #     for i in range(1,13) :
    #         lp,created = LockerPort.objects.get_or_create(lockerid = obj, portid = i)
    self.message_user(request, "Copy setting parameter successfully")
copy_setting_parameter.short_description = "Copy Parameter Setting to new slot"

def delete_setting_parameter(self, request, queryset):
    for obj_tester_slot in queryset:
        obj_tester_slot.limittester_list.all().delete()

    self.message_user(request, "Delete all setting parameter successfully")
delete_setting_parameter.short_description = "Delete all parameter setting"


class TesterAdmin(admin.ModelAdmin):
    search_fields = ['station','name']
    list_filter = [('station',RelatedOnlyFieldListFilter),'name','spc_control']
    list_display = ('name','station','slot','setting_count','spc_control','spc_ordering')
    fieldsets = [
        (None,               {'fields': ['name','station','slot','spc_control','spc_ordering']}),
    ]
    actions = [create_parameter_setting,copy_setting_parameter,delete_setting_parameter]

    # inlines = [ComponentsTrackingInline]
    # def get_queryset(self, request):
    # # def queryset(self, request): # For Django <1.6
    #     qs = super(TesterAdmin, self).get_queryset(request)
    #     # qs = super(CustomerAdmin, self).queryset(request) # For Django <1.6
    #     qs = qs.order_by('station')
    #     return qs

    # def queryset(self, request):
    #     if request.user.is_superuser:
    #         return Entry.objects.all()
    #     return Entry.objects.filter(author=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super(TesterAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['station'].queryset = Station.objects.filter(spc_control=True)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "station":
            kwargs["queryset"] = Station.objects.order_by('family','station')
        return super(TesterAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    inlines = [TesterParameterLimitAdminInline]
    
admin.site.register(Tester,TesterAdmin)

