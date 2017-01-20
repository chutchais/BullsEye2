from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import xml.etree.cElementTree as ET
from django.http import HttpResponse

from .serializers import BomSerializer

from django.shortcuts import render
from .forms import StationModelForm
from .forms import DashboardForm
from .forms import ReportFiltersForm
from .forms import SpcFilterForm

from django.http import HttpResponseRedirect
from django.views.generic import CreateView

from .forms import BomDetailsFormSet, BomForm,snTrackingForm
from .models import Bom
from .models import Family
from .models import Product
from .models import Station
from .models import WorkOrder
from .models import WorkOrderDetails
from django.contrib.auth.models import User
from .models import Performing
from .models import PerformingDetails
from .models import Parameter
from .models import Components
from .models import ComponentsTracking

from datetime import datetime, timedelta
from django.db.models import Count,Sum
from django.db import models

import json
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta

def get_family(request):
    #campus = models.Campus.objects.get(pk=campus_id)
    fam = Family.objects.filter(critical=True).order_by('name')
    family_dict = {}
    for f in fam:
        family_dict[f.name] = f.name
    return HttpResponse(json.dumps(family_dict))

def get_station(request, family):
    #campus = models.Campus.objects.get(pk=campus_id)
    stations = Station.objects.filter(family__name=family,critical=True).order_by('ordering')
    station_dict = {}
    for station in stations:
        station_dict[station.station] = station.name
    return HttpResponse(json.dumps(station_dict))
# , mimetype="application/json"

def get_product(request, family):
    #campus = models.Campus.objects.get(pk=campus_id)
    products = Product.objects.filter(family__name=family).order_by('name')
    product_dict = {}
    for product in products:
        product_dict[product.name] = product.model
    return HttpResponse(json.dumps(product_dict))

def get_parameter(request, station):
    #campus = models.Campus.objects.get(pk=campus_id)
    parameters = Parameter.objects.filter(group=station,critical=True).order_by('ordering')
    parameter_dict = {}
    for parameter in parameters:
        parameter_dict[parameter.name] = parameter.name
    print (parameter_dict)
    return HttpResponse(json.dumps(parameter_dict))

# Dashboard .
def index(request):
    form = DashboardForm(request.POST or None)
   
    if form.is_valid():
        report_date = form.cleaned_data["report_date"]
        #start at 0:00am
        report_date2= datetime.strftime(report_date,"%Y-%m-%d")
        start_date = datetime.combine(report_date, datetime.min.time())# +timedelta(hours=6)
        stop_date = start_date +timedelta(days=1)
        #a = datetime.combine(start_date, datetime.min.time())#datetime.strptime(start_date,"%Y-%m-%d")
        
    else:
        from datetime import date
        d = date.today()
        report_date2= datetime.strftime(d,"%Y-%m-%d")
        start_date = datetime.combine(d, datetime.min.time()) #+timedelta(hours=6)
        stop_date = start_date +timedelta(days=1)

    # d1=datetime.strftime(start_date,"%Y-%m-%d %I:%M:%S")
    # d2=datetime.strftime(stop_date,"%Y-%m-%d %I:%M:%S")
    d1=datetime.strftime(start_date,"%Y-%m-%d")
    d2=datetime.strftime(stop_date,"%Y-%m-%d")

    from django.utils import timezone
    current_tz = timezone.get_current_timezone()


    d1 =current_tz.localize(start_date )
    d2 =current_tz.localize (stop_date )


    print ('Index page : %s' % d1)
    print ('Index page : %s' % d2)

    total_input=get_total_input(d1,d2)
    total_output=get_total_output(d1,d2)
    total_shipped=get_total_shipped(d1,d2)
    total_scrapped=get_total_scrapped(d1,d2)
    input_details=get_input_by_product(d1,d2)
    output_details=get_output_by_product(d1,d2)
    yield_details=get_yield(d1,d2)
    wip_details=get_wip()
    stock_details=get_stock()
    shipped_details=get_ship(d1,d2)
    
    data={
            "date" : report_date2,
            "title":start_date,
            "total_input":total_input,
            "total_output":total_output,
            "total_scrapped":total_scrapped,
            "ete_yield":(total_output/total_input)*100 if total_input>0 else 0,
            "wip":get_total_wip(),
            "stock": get_total_stock(),
            "shipped" : total_shipped,
            "input_details":input_details,
            "output_details": output_details,
            "yield_details":yield_details,
            "wip_details":wip_details,
            "stock_details":stock_details,
            "shipped_details":shipped_details,
    }

    context ={
        "data": data,
        "form": form
    }
    return render(request, 'production/dashboard_today.html',context)

#Production functions
def get_total_input(start_date,end_date):
    #wd=WorkOrderDetails.objects.filter(created_date__range=[start_date,end_date])
    #input must check from First Station.
    p=Performing.objects.filter(station__first_process=True,started_date__range=[start_date,end_date])
    return p.count()

def get_total_output(start_date,end_date):
    wd=WorkOrderDetails.objects.filter(modified_date__range=[start_date,end_date],status='DONE')
    return wd.count()

def get_total_shipped(start_date,end_date):
    wd=WorkOrderDetails.objects.filter(modified_date__range=[start_date,end_date],status='SHIPPED')
    return wd.count()

def get_total_scrapped(start_date,end_date):
    wd=WorkOrderDetails.objects.filter(modified_date__range=[start_date,end_date],status='SCRAPPED')
    return wd.count()

def get_total_wip():
    wd=WorkOrderDetails.objects.filter(status='IN')
    return wd.count()

def get_total_stock():
    wd=WorkOrderDetails.objects.filter(status='DONE')
    return wd.count()

def get_input_by_product(start_date,end_date):
    # p = Product.objects.filter(workorder_used__sn_list__created_date__range=
    #     [start_date,end_date]).annotate(number=Count('name'))
    p = Product.objects.filter(workorder_used__sn_list__performing_list__started_date__range=
        [start_date,end_date],workorder_used__sn_list__performing_list__station__first_process=True).annotate(number=Count('name'))
    return p

def get_output_by_product(start_date,end_date):
    p = Product.objects.filter(workorder_used__sn_list__modified_date__range=
        [start_date,end_date],workorder_used__sn_list__status='DONE').annotate(number=Count('name'))
    return p

def get_yield(start_date,end_date):
    from django.db.models import Count,Sum,Value, When,Case,IntegerField,CharField
    p = Performing.objects.filter(started_date__range=[start_date,end_date],loop=1).values('station__station').annotate(number=Count('sn_wo'),
        passed=Sum(Case(When(result=True,then=Value(1)),default=Value(0),output_field=IntegerField())),
        failed=Sum(Case(When(result=False,then=Value(1)),default=Value(0),output_field=IntegerField())),
        prime=Sum(Case(When(loop = 1,then=Value(1)),default=Value(0),output_field=IntegerField())),
        retest=Sum(Case(When(loop__gt = 1,then=Value(1)),default=Value(0),output_field=IntegerField())))#.order_by('-number')[:5]
    return p


def get_wip():
    from django.db.models import Count,Sum,Value, When,Case,IntegerField,CharField
    wip = WorkOrderDetails.objects.filter(status='IN').values('workorder__product__family__name').annotate(number=Count('sn'))
    return wip

def get_stock():
    from django.db.models import Count,Sum,Value, When,Case,IntegerField,CharField
    stock = WorkOrderDetails.objects.filter(status='DONE').values('workorder__product__family__name').annotate(number=Count('sn'))
    return stock

def get_ship(start_date,end_date):
    shipped = Product.objects.filter(workorder_used__sn_list__modified_date__range=
        [start_date,end_date],workorder_used__sn_list__status='SHIPPED').annotate(number=Count('name'))
    return shipped

#Daily Load/Input
def load_by_date(request,load_date):
    d1 = datetime.strptime(load_date,"%Y-%m-%d")
    d2 = d1 +timedelta(days=1)
    print (d1)
    print (d2)

    total_input_product=get_input_by_product(d1,d2)
    total_input_family=get_input_by_family(d1,d2)

    data ={
        "date" : load_date,
        "title" : "Loading details : ",
        "number_by_product": total_input_product,
        "number_by_family": total_input_family
    }
    context ={
        "data": data,
    }
    return render(request, 'production/dashboard_today_details.html',context)

def get_input_by_family(start_date,end_date):
    f = Family.objects.filter(product_used__workorder_used__sn_list__performing_list__started_date__range=
        [start_date,end_date],product_used__workorder_used__sn_list__performing_list__station__first_process=True).annotate(number=Count('name'))
    return f

def get_input_by_workorder(start_date,end_date):
    w = WorkOrder.objects.filter(sn_list__performing_list__started_date__range=
        [start_date,end_date],sn_list__performing_list__station__first_process=True).annotate(number=Count('name'))
    return w
#End - Daily Load/Input


#Daily by Status
def status_by_date(request,report_date,status):
    d1 = datetime.strptime(report_date,"%Y-%m-%d")
    d2 = d1 +timedelta(days=1)
    print (d1)
    print (d2)

    if status =='NEW':
        total_product=get_input_by_product(d1,d2)
        total_family=get_input_by_family(d1,d2)
        total_workorder= get_input_by_workorder(d1,d2)
    else:
        total_product=get_unit_by_product(d1,d2,status)
        total_family=get_unit_by_family(d1,d2,status)
        total_workorder=get_unit_by_workorder(d1,d2,status)

    if status=='IN':
        title="Today WIP unit details"
    elif status=='DONE':
        title="Completed unit details"
    elif status=='NEW':
        title="Loading unit details"
    elif status=='WIP':
        title="WIP unit details"
    else :
        title ="Shipped unit details"

    data ={
        "date" : report_date,
        "title" : title,
        "status" : status,
        "number_by_product": total_product,
        "number_by_family": total_family,
        "number_by_workorder": total_workorder
    }
    context ={
        "data": data,
    }
    return render(request, 'production/dashboard_today_details.html',context)

def status_all(request,status):

    total_product=get_all_by_product(status)
    total_family=get_all_by_family(status)
    total_workorder=get_all_by_workorder(status)

    if status=='IN':
        title="All WIP unit details"
    elif status=='DONE':
        title="All Completed unit details"
    elif status=='NEW':
        title="All Loading unit details"
    else :
        title ="All Shipped unit details"

    data ={
        "date" : "",
        "title" : title,
        "status" : status,
        "number_by_product": total_product,
        "number_by_family": total_family,
        "number_by_workorder": total_workorder
    }
    context ={
        "data": data,
    }
    return render(request, 'production/dashboard_today_details.html',context)

def wip_master(request,status):
    total_product=get_all_by_product(status)
    total_family=get_all_by_family(status)
    total_workorder=get_all_by_workorder(status)
    print (status)
    if status=='IN':
        title="All WIP unit details"
    elif status=='DONE':
        title="All Completed unit details"
    elif status=='NEW':
        title="All Loading unit details"
    else :
        title ="All Shipped unit details"

    data ={
        "date" : "",
        "title" : title,
        "status" : status,
        "number_by_product": total_product,
        "number_by_family": total_family,
        "number_by_workorder": total_workorder
    }
    context ={
        "data": data,
    }
    return render(request, 'production/wip_master.html',context)

def wip_details(request,status,groupby,value):
    print ('on WIP details %s' % status)
    wip_details=get_wip_by_station(status,groupby,value)

    if status=='IN':
        title="All WIP unit details"
    elif status=='DONE':
        title="All Completed unit details"
    elif status=='NEW':
        title="All Loading unit details"
    else :
        title ="All Shipped unit details"

    data ={
        "date" : "",
        "title" : title,
        "status" : status,
        "groupby" : groupby,
        "keyvalue" :value,
        "wip_details": wip_details,
    }
    context ={
        "data": data,
    }
    return render(request, 'production/wip_details.html',context)

def wip_serial(request,status,groupby,keyvalue,station):
    print ('on WIP-Serial details %s' % station)
    wip_serials=get_serial_wip_by_station(status,groupby,keyvalue,station)

    if status=='IN':
        title="All WIP unit details"
    elif status=='DONE':
        title="All Completed unit details"
    elif status=='NEW':
        title="All Loading unit details"
    else :
        title ="All Shipped unit details"

    data ={
        "date" : "",
        "title" : title,
        "status" : status,
        "groupby" : groupby,
        "keyvalue" :keyvalue,
        "sn_list": wip_serials,
    }
    context ={
        "data": data,
    }
    return render(request, 'production/dashboard_sn_list.html',context)

def get_serial_wip_by_station(status,groupby,keyvalue,station):
    if groupby=='family':
        kwargs = {
        'workorder__product__family__name': keyvalue,
        'current_station__station':station,
        'status':status,
        }
        print (kwargs)
        s=WorkOrderDetails.objects.filter(**kwargs)
    elif groupby=='product':
        kwargs = {
        '{0}__{1}__{2}__name'.format('sn_current_station','workorder', 'product'): keyvalue,
        'sn_current_station__status':status,
        'station':station,
        }
        f=Product.objects.get(name=keyvalue)
        s=Station.objects.filter(family=f.family).annotate(number=Sum(models.Case(models.When(**kwargs,then=1),default=0,output_field=models.IntegerField()))).order_by('station').exclude(number=0)
    else:
        kwargs = {
        '{0}__{1}__name'.format('sn_current_station','workorder'): keyvalue,
        'sn_current_station__status':status,
        'station':station,
        }
        w=WorkOrder.objects.get(name=keyvalue)
        s=Station.objects.filter(family=w.product.family).annotate(number=Sum(models.Case(models.When(**kwargs,then=1)
            ,default=0,output_field=models.IntegerField()))).order_by('station').exclude(number=0)
    return s

def get_wip_by_station(status,groupby,keyvalue):
    if groupby=='family':
        kwargs = {
        '{0}'.format('family'): keyvalue,
        'sn_current_station__status':status,
        }
        s=Station.objects.filter(**kwargs).annotate(number=Count('sn_current_station')).order_by('station')
    elif groupby=='product':
        kwargs = {
        '{0}__{1}__{2}__name'.format('sn_current_station','workorder', 'product'): keyvalue,
        'sn_current_station__status':status,
        }
        f=Product.objects.get(name=keyvalue)
        s=Station.objects.filter(family=f.family).annotate(number=Sum
            (models.Case(models.When(**kwargs,then=1)
                ,default=0,output_field=models.IntegerField()))).order_by('station').exclude(number=0)
    else:
        kwargs = {
        '{0}__{1}__name'.format('sn_current_station','workorder'): keyvalue,
        'sn_current_station__status':status,
        }
        w=WorkOrder.objects.get(name=keyvalue)
        s=Station.objects.filter(family=w.product.family).annotate(number=Sum
            (models.Case(models.When(**kwargs,then=1)
                ,default=0,output_field=models.IntegerField()))).order_by('station').exclude(number=0)
    return s




def get_unit_by_workorder(start_date,end_date,status):
    w = WorkOrder.objects.filter(sn_list__modified_date__range=
        [start_date,end_date],sn_list__status=status).annotate(number=Count('name'))
    return w

def get_unit_by_product(start_date,end_date,status):
    p = Product.objects.filter(workorder_used__sn_list__modified_date__range=
        [start_date,end_date],workorder_used__sn_list__status=status).annotate(number=Count('name'))
    return p

def get_unit_by_family(start_date,end_date,status):
    f = Family.objects.filter(product_used__workorder_used__sn_list__modified_date__range=
        [start_date,end_date],product_used__workorder_used__sn_list__status=status).annotate(number=Count('name'))
    return f

#WIP - Total (no datetime)
def get_all_by_workorder(status):
    w = WorkOrder.objects.filter(sn_list__status=status).annotate(number=Count('sn_list'))
    return w

def get_all_by_product(status):
    p = Product.objects.filter(workorder_used__sn_list__status=status).annotate(number=Count('name'))
    return p

def get_all_by_family(status):
    f = Family.objects.filter(product_used__workorder_used__sn_list__status=status).annotate(number=Count('name'))
    return f
#End - #Daily by Status



#Sn list by Status
def snlist_by_status_date(request,report_date,status):
    d1 = datetime.strptime(report_date,"%Y-%m-%d")
    d2 = d1 +timedelta(days=1)
    print (d1)
    print (d2)

    if status=='IN':
        title="Serial number list for Today WIP"
    elif status=='DONE':
        title="Serial number list of completed unit"
    else :
        title ="Serial number list of Shipped unit"

    if status=='NEW':
        status='IN'
        sn_list = get_new_sn_list(d1,d2,status)
    else:
        sn_list = get_sn_list(d1,d2,status)

    data ={
        "date" : report_date,
        "title" : title,
        "status" : status,
        "sn_list": sn_list,
    }
    context ={
        "data": data,
    }
    return render(request, 'production/dashboard_sn_list.html',context)


def snlist_by_status_date_parameter(request,report_date,status,groupby,value):
    d1 = datetime.strptime(report_date,"%Y-%m-%d")
    d2 = d1 +timedelta(days=1)
    print (d1)
    print (d2)

    if status=='IN':
        title="Serial number list for Today WIP"
    elif status=='DONE':
        title="Serial number list of completed unit"
    else :
        title ="Serial number list of Shipped unit"

    if status=='NEW':
        status='IN'
        sn_list = get_newload_sn_list_w_parameter(d1,d2,status,groupby,value)
        template_file='production/dashboard_loadsn_list.html'
    else:
        sn_list = get_sn_list_w_parameter(d1,d2,status,groupby,value)
        template_file='production/dashboard_sn_list.html'

    data ={
        "date" : report_date,
        "title" : title,
        "status" : status,
        "sn_list": sn_list,
    }
    context ={
        "data": data,
    }
    return render(request, template_file,context)

def get_sn_list(start_date,end_date,status):
    sns = WorkOrderDetails.objects.filter(modified_date__range=
        [start_date,end_date],status=status)
    return sns

def get_new_sn_list(start_date,end_date,status):
    sns = WorkOrderDetails.objects.filter(created_date__range=
        [start_date,end_date],status=status)
    return sns

#End - #Sn list by Status

def get_sn_list_w_parameter(start_date,end_date,status,groupby,keyvalue):
    
    if groupby=='family':
        kwargs = {
        '{0}__{1}__{2}__name'.format('workorder', 'product','family'): keyvalue,
        'status':status,
        '{0}__range'.format('created_date' if status=='IN' else 'modified_date') :[start_date,end_date]
        }
    elif groupby=='product':
        kwargs = {
        '{0}__{1}__name'.format('workorder', 'product'): keyvalue,
        'status':status,
        '{0}__range'.format('created_date' if status=='IN' else 'modified_date') :[start_date,end_date]
        }
    else:
        kwargs = {
        '{0}__name'.format('workorder'): keyvalue,
        'status':status,
        '{0}__range'.format('created_date' if status=='IN' else 'modified_date') :[start_date,end_date]
        }
    print (kwargs)
    # sns = WorkOrderDetails.objects.filter(modified_date__range=
    #     [start_date,end_date],status=status,**kwargs)
    sns = WorkOrderDetails.objects.filter(**kwargs)
    return sns

def get_newload_sn_list_w_parameter(start_date,end_date,status,groupby,keyvalue):
    
    if groupby=='family':
        kwargs = {
        '{0}__{1}__{2}__{3}__name'.format('sn_wo', 'workorder','product','family'): keyvalue,
        'station__first_process':True,
        '{0}__range'.format('started_date' if status=='IN' else 'modified_date') :[start_date,end_date]
        }
    elif groupby=='product':
        kwargs = {
        '{0}__{1}__{2}__name'.format('sn_wo', 'workorder','product'): keyvalue,
        'station__first_process':True,
        '{0}__range'.format('started_date' if status=='IN' else 'modified_date') :[start_date,end_date]
        }
    else:
        kwargs = {
        '{0}__{1}__name'.format('sn_wo', 'workorder'): keyvalue,
        'station__first_process':True,
        '{0}__range'.format('started_date' if status=='IN' else 'modified_date') :[start_date,end_date]
        }
    print (kwargs)
    # sns = WorkOrderDetails.objects.filter(modified_date__range=
    #     [start_date,end_date],status=status,**kwargs)
    sns = Performing.objects.filter(**kwargs)
    return sns

def dashboard2(request):
    data={
        "title":"test Title",
        "author":"test Author",
        "pub_date":"July 23,2016",
        "body":"Have a good day",
    }
    context ={
        "press": data
    }
    return render(request, 'production/dashboard2.html',context)

def dashboard3(request):
    form = DashboardForm(request.POST or None)
    data={
        "title":"test Title",
        "author":"test Author",
        "pub_date":"July 23,2016",
        "body":"Have a good day",
    }
    context ={
        "press": data,
        "form" : form
    }
    return render(request, 'production/testdt.html',context)

def spc_main(request):
    form = ReportFiltersForm(request.POST or None)
    import datetime

    if form.is_valid():
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        start_date= datetime.datetime.strftime(start_date,"%Y-%m-%d")
        stop_date = datetime.datetime.strftime(end_date,"%Y-%m-%d")
       
    else:
        from datetime import date
        default_start = date.today()  - datetime.timedelta(days=7)
        start_date= datetime.datetime.strftime(default_start,"%Y-%m-%d")
        #date_stop = date.today() +datetime.timedelta(days=1)
        stop_date = datetime.datetime.strftime(date.today(),"%Y-%m-%d")

    print (start_date)
    print (stop_date)


    data={
        "title":"Production Distribution Data",
        "date_from_str":start_date,
        "date_to_str":stop_date,
        "date_from":start_date,
        "date_to":stop_date,
    }

    from django.utils import timezone
    current_tz = timezone.get_current_timezone()
    
    date_from = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    date_to = datetime.datetime.strptime(stop_date,'%Y-%m-%d')

    date_from=current_tz.localize(date_from )
    date_to =current_tz.localize (date_to )

    st=Station.objects.filter(critical=True)
    # p = Performing.objects.filter(finished_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
    #     finished_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
    #     station__critical=True)
    p = Performing.objects.filter(finished_date__range=[date_from,date_to],
        station__critical=True)

    context ={
        "data": data,
        "station" : st,
        "performing" :p,
        "form" : form
    }
    return render(request, 'production/spc_main_graph.html',context)

def spc_main_graph(request,family=''):
    form = ReportFiltersForm(request.POST or None)
    import datetime
    qmode ='7day'

    if form.is_valid():
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        start_date= datetime.datetime.strftime(start_date,"%Y-%m-%d")
        stop_date = datetime.datetime.strftime(end_date,"%Y-%m-%d")
       
    else:
        from datetime import date
        if qmode=='7day':
            default_start = date.today() - datetime.timedelta(days=7)
        elif qmode=='14day':
            default_start = date.today() - datetime.timedelta(days=14)
        elif qmode=='8week':
            default_start = date.today() - datetime.timedelta(days=56)
        elif qmode=='4month':
            default_start = date.today() - datetime.timedelta(months=4)
        else:
            default_start = date.today() - datetime.timedelta(days=7)

        start_date= datetime.datetime.strftime(default_start,"%Y-%m-%d")
        stop_date = datetime.datetime.strftime(date.today(),"%Y-%m-%d")

    # print (start_date)
    # print (stop_date)
    date_from = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    date_to = datetime.datetime.strptime(stop_date,'%Y-%m-%d')

    objfamily = Family.objects.filter(critical=True).order_by('ordering')

    if family=='':
        family = objfamily[0].name

    st=Station.objects.filter(critical=True,family__name=family).order_by('ordering')
    params = Parameter.objects.filter(critical=True).order_by('ordering')

    data={
        "title":"Production Distribution Data",
        "date_from_str":start_date,
        "date_to_str":stop_date,
        "date_from":start_date,
        "date_to":stop_date,
        "family" : family,
        "mode" : qmode
    }

    context ={
        "data": data,
        "station" : st,
        "parameter" :params,
        "family" : objfamily,
        "form" : form
    }
    return render(request, 'production/spc_main_graph.html',context)


def spc_filter(request):
    form = SpcFilterForm(request.POST or None)
    import datetime

    if form.is_valid():
        start_date = form.cleaned_data["start_date"]
        # end_date = form.cleaned_data["end_date"]
        # start_date= datetime.datetime.strftime(start_date,"%Y-%m-%d")
        # stop_date = datetime.datetime.strftime(end_date,"%Y-%m-%d")
       
    else:
        from datetime import date
        start_date= datetime.datetime.strftime(date.today(),"%Y-%m-%d")
    #     date_stop = date.today() +timedelta(days=1)
    #     stop_date = datetime.datetime.strftime(date_stop,"%Y-%m-%d")

    # print (start_date)
    # print (stop_date)


    data={
        "title":"Select criteria for Distribution data",
        "date_from_str":'start_date',
        "date_to_str":'stop_date',
        "date_from":'start_date',
        "date_to":'stop_date',
    }


    context ={
        "data": data,
        "form" : form
    }
    return render(request, 'production/spc_selection.html',context)


@api_view(['GET', 'POST'])
def spc_cpk_station(request,family,station,parameter,date_range):
    

    import datetime
    from django.db.models import F
    from django.db.models import Count,Max,Min,Avg,StdDev

    from datetime import date
    qmode=date_range
    if qmode=='7day':
        default_start = date.today() - datetime.timedelta(days=7)
    elif qmode=='14day':
        default_start = date.today() - datetime.timedelta(days=14)
    elif qmode=='8week':
        default_start = date.today() - datetime.timedelta(days=56)
    elif qmode=='4month':
        default_start = date.today() - datetime.timedelta(months=4)
    else:
        default_start = date.today() - datetime.timedelta(days=7)

    start_date= datetime.datetime.strftime(default_start,"%Y-%m-%d")
    stop_date = datetime.datetime.strftime(date.today(),"%Y-%m-%d")

    # print (start_date)
    # print (stop_date)
    date_from = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    date_to = datetime.datetime.strptime(stop_date,'%Y-%m-%d')

    data={
        "title":"Production Data",
        "family": family,
        "station" : station,
        "date_from_str":date_from,
        "date_to_str":date_to,
        "date_from":date_from,
        "date_to":date_to,
    }

    # date_from = datetime.datetime.strptime(date_from,'%Y-%m-%d')
    # date_to = datetime.datetime.strptime(date_to,'%Y-%m-%d')

    pd2 = PerformingDetails.objects.filter(
    performing__started_date__range=[date_from,date_to],
    parameter__name =parameter,
    performing__sn_wo__workorder__product__family__name=family,
    performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min')).values('parameter__name').annotate(total=Count('value'),min=Min('value'),
        max=Max('value'),avg=Avg('value'),std=StdDev('value'),
        limit_min=Max('limit_min'),limit_max=Max('limit_max'))
    # pd2 = PerformingDetails.objects.filter(
    # performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
    # performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
    # parameter__critical=True,
    # performing__sn_wo__workorder__product__family__name=family,
    # performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min')).values('parameter__name').annotate(total=Count('value'),min=Min('value'),
    #     max=Max('value'),avg=Avg('value'),std=StdDev('value'),
    #     limit_min=Max('limit_min'),limit_max=Max('limit_max'))

    record_count = pd2.count()

    context ={
        "data": data,
        "performing" :pd2,
    }
    return render(request, 'production/spc_station.html',context)


@api_view(['GET', 'POST'])
def spc_station(request,family,station,date_from,date_to):
    data={
        "title":"Production Data",
        "family": family,
        "station" : station,
        "date_from_str":date_from,
        "date_to_str":date_to,
        "date_from":date_from,
        "date_to":date_to,
    }

    import datetime
    from django.db.models import F
    from django.db.models import Count,Max,Min,Avg,StdDev

    date_from = datetime.datetime.strptime(date_from,'%Y-%m-%d')
    date_to = datetime.datetime.strptime(date_to,'%Y-%m-%d')

    pd2 = PerformingDetails.objects.filter(
    performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
    performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
    parameter__critical=True,
    performing__sn_wo__workorder__product__family__name=family,
    performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min')).values('parameter__name').annotate(total=Count('value'),min=Min('value'),
        max=Max('value'),avg=Avg('value'),std=StdDev('value'),
        limit_min=Max('limit_min'),limit_max=Max('limit_max'))

    record_count = pd2.count()

    context ={
        "data": data,
        "performing" :pd2,
    }
    return render(request, 'production/spc_station.html',context)

@api_view(['GET', 'POST'])
def get_process(request,station,family):
    try :
        a = Station.objects.get(station=station,family=family)
        return HttpResponse("%s" % a.process)
    except Exception as e:
        return HttpResponse("")
    


def post_list(request):
    title ="Welcome"
    form = StationModelForm(request.POST or None)
    context ={
        "title": title,
        "form" : form
    }
    if form.is_valid():
        instance = form.save(commit=False)
        station = form.cleaned_data["station"]
        instance.save()
        context ={
            "title": "Sign up successful!!"
        }   
        # if not station :
        #   station = "new station"
        #   instance.station = station
        #   instance.save()
        #   context ={
        #   "title": "Sign up successful!!",
        #   }

    return render(request, 'production/post_list.html',context)

        # if form.is_valid():
        #   instance = form.save(commit=False)
        #   station = form.cleaned_data["station"]
        #   if not station:
        #       station = "new station"
        #       instance.station = station
        #       instance.save()
        #       context ={
        #       "title": "Sign up successful!!",
        #       }

    # if a GET (or any other method) we'll create a blank form
    # else:
    #     form = StationModelForm()


class RecipeCreateView(CreateView):
    template_name = 'bom_add.html'
    model = Bom
    form_class = BomForm
    success_url = 'success/'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        bomdetail_form = BomDetailsFormSet()
        return self.render_to_response(
            self.get_context_data(
                form=form,bomdetail_form=bomdetail_form))


@api_view(['GET', 'POST'])
def getBOM(request):
    """
    Get, all BOM data
    """
    try:
        bomData = Bom.objects.all ()

    except bomData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BomSerializer(bomData, many=True)
        return Response(serializer.data )


@api_view(['GET', 'POST'])
def upload_fits(request):

    if True :
        xml = request.body
        return Response(execute_transaction(xml))
    else:
        return Response("Accept only xml (ODC/SPC compatible)" )

def execute_transaction(xml):
    try:
        root = ET.fromstring(xml)
        #Main data
        sn = root.findtext('serialnumber')
        trans_seq = root.findtext('trans_seq')
        sn_attr_code = root.findtext('sn_attr_code')
        operation = root.findtext('operation')
        operation_name = root.findtext('operationname')
        employee = root.findtext('employee')
        shift = root.findtext('shift')
        buildtype= root.findtext('buildtype')
        runtype= root.findtext('runtype')
        partnumber= root.findtext('partnumber')
        workorder= root.findtext('workorder')
        model= root.findtext('model')
        tester =  root.findtext('tester')
        next_operation=root.findtext('next_operation')
        
        if model=='':
            vFamily =WorkOrder.objects.get(name=workorder)
            if vFamily:
                model= vFamily.product.family.name

        datetimein= root.findtext('datetimein')
        datetimeout= root.findtext('datetimeout')
        if datetimeout is None:
            datetimeout = datetimein

        datetimeout = datetimein if datetimeout=='' else datetimeout

        

        #result=root.findtext('result')
        result=root.findtext('parameters/parameter[@code="1101"]')
        if result is None:
            result='PASS'#root.findtext('parameters/parameter[@code="1101"]')

        

        #dispose code
        dispose_code = root.findtext('disposecode')

        updateResult = True if (result == 'PASS' or dispose_code=='SHIPPED') else  False

        #if dispose code=SHIPPED , need to update status on WorkOrderDetails.status=SHIPPED
        # status_update= 'SHIPPED' if dispose_code=='SHIPPED' else 'IN'
        # updateResult = True if dispose_code=='SHIPPED' else  updateResult

        if dispose_code=='SHIPPED':
            status_update='SHIPPED'
            updateResult=True
        elif dispose_code=='SCRAPED':
            status_update='SCRAPED'
            updateResult=False
        else :
            status_update='IN'
        ###############################################################

        #check Master data and create object
        #1)Family
        objFamily,created = Family.objects.get_or_create(name=model)
        #2)Bom
        objBom,created = Bom.objects.get_or_create(name=partnumber,model=partnumber,rev='00')
        #3)Product
        # objProduct,created = Product.objects.get_or_create(name=partnumber,model=partnumber,rev='00',
        #     bom=objBom,family=objFamily)
        #Fix same product located on multiple Family -- Aug 23,2016
        objProduct,created = Product.objects.get_or_create(name=partnumber,model=partnumber,rev='00')
        objProduct.bom=objBom
        objProduct.family=objFamily
        objProduct.save()

        #4)Station/Operation
        objStation,created = Station.objects.get_or_create(station=operation,family=objFamily)
        #update sation name/description
        if created :
            objStation.name=operation_name
            objStation.description=objStation.name
            objStation.save()


        #5)WorkOrder
        objWorkorder,created = WorkOrder.objects.get_or_create(name=workorder,product=objProduct)
        #6)User
        objUser,created = User.objects.get_or_create(username=employee,password=employee,
            email=("%s@fabrinet.co.th" % employee ))
        #7)Workorder and WorkorderDetail
        objWorkOrder,created = WorkOrder.objects.get_or_create(name=workorder,product=objProduct)
        # objSnWoDetails,created = WorkOrderDetails.objects.update_or_create(sn=sn,workorder=objWorkorder,
        #     user=objUser,status=status_update,defaults={"current_staton":operation,"result":updateResult})

        

        #8)Performing
        import datetime
        d1 = datetime.datetime.strptime(datetimein,"%m/%d/%Y %I:%M:%S %p")
        datein=d1.strftime("%Y-%m-%d %I:%M:%S") # Store this!
        d2 = datetime.datetime.strptime(datetimeout,"%m/%d/%Y %I:%M:%S %p")
        dateout=d2.strftime("%Y-%m-%d %I:%M:%S") # Store this!

        #Time zone handle
        from django.utils import timezone
        dateinTz = timezone.make_aware(d1, timezone.get_default_timezone())
        dateoutTz = timezone.make_aware(d2, timezone.get_default_timezone())

        objSnWoDetails,created = WorkOrderDetails.objects.update_or_create(sn=sn,workorder=objWorkorder,
            defaults={"result":updateResult,"user":objUser,"status":status_update,"modified_date":datein})

        if created :
            objSnWoDetails.created_date = dateinTz#datein
            objSnWoDetails.modified_date = dateinTz#datein

        objSnWoDetails.last_station=objStation#objSnWoDetails.current_station

        #Need to modify based on Routing
        objNextStation,created = Station.objects.get_or_create(station=next_operation,family=objFamily)
        objSnWoDetails.current_station=objNextStation
        #End Modify

        objSnWoDetails.status = 'DONE' if objStation.last_process else objSnWoDetails.status
        objSnWoDetails.status = 'SHIPPED' if status_update=='SHIPPED' else objSnWoDetails.status
        objSnWoDetails.save()


        #8.1) check and get Loop
        objLoop = Performing.objects.filter(sn_wo=objSnWoDetails,station=objStation).count()
        #8.2)Add Performing
        objPerforming = Performing.objects.create(sn_wo=objSnWoDetails,station=objStation,
            started_date=dateinTz,finished_date=dateoutTz,result=updateResult,user=objUser,
            dispose_code=dispose_code,loop=objLoop+1,tester=tester)

        #9)PerformingDetails
        #Fits details (parameter)
        for paramElement in root.findall('parameters/parameter'):
            code = paramElement.attrib['code']
            description = paramElement.attrib['desc']
            value = paramElement.text
            #new attribute --by Chutchai on Sep 27,2016
            min_limit= 0 if paramElement.attrib['min']=="" else paramElement.attrib['min']
            max_limit=0 if paramElement.attrib['max']=="" else paramElement.attrib['max']
            param_result=paramElement.attrib['result']

            each_result = True if param_result=='Passed' else False
            #9.1)Parameter
            #Edit by Chutchai S on Nov 10,2016 -- To fix same parameter for many operation
            objParam,created = Parameter.objects.get_or_create(name=code,group=operation)
            if created:
                objParam.description=description
                objParam.save()

            if objParam.activated :
                #To put data into Value field
                objPerformingDetails =PerformingDetails.objects.create(performing=objPerforming,parameter=objParam,
                    value_str=value,result=each_result,created_date=dateinTz,user=objUser,
                    limit_min=min_limit,limit_max=max_limit)
                if is_Float(value):
                    objPerformingDetails.value=float(value)
                    objPerformingDetails.save()

        #10)Component tracking
        for partElement in root.findall('components/part'):
            #part master
            part_id = partElement.attrib['part_id']
            part_no = partElement.attrib['part_no']
            mfg_partno = partElement.attrib['mfg_partno']
            mfg_datecode = partElement.attrib['mfg_datecode']
            mfg_lotcode = partElement.attrib['mfg_lotcode']
            mfg_name = partElement.attrib['mfg_name']
            rtno = partElement.attrib['rtno']
            #part details
            rd = partElement.attrib['rd']
            part_sn = partElement.text
            #10.1)Add Part master to Components
            objComponent,created=Components.objects.get_or_create(part_id=part_id)
            if created:
                objComponent.part_no=part_no
                objComponent.mfg_partno=part_no
                objComponent.mfg_datecode=mfg_datecode
                objComponent.mfg_lotcode=mfg_lotcode
                objComponent.mfg_name=mfg_name
                objComponent.rtno=rtno
                objComponent.save()
            #10.2)Add Part details
            objPart = ComponentsTracking.objects.create(part=objComponent,sn_wo=objSnWoDetails,rd=rd,
                station=objStation,user=objUser)


        return ("Successful")

    except Exception as e:
        return "Failed : Unable to insert transaction %s" % e.args[0]


def is_Float(x):
    try:
        x=float(x)
        return True
    except :
        return False

#SN tracking#
def unit_tracking(request,sn):
    form = snTrackingForm(request.POST or None ,initial={'sn': sn})
    queryset=None
    if form.is_valid():
        sn = form.cleaned_data["sn"]
            #print (sn)
        
    queryset=Performing.objects.filter(sn_wo__sn=sn)
    # components=ComponentsTracking.objects.filter(sn_wo__sn=sn)

    data ={
        "sn" : sn,
        "title" : "Serial number tracking",
        "queryset" : queryset
    }
    context ={
        "data": data,
        "form" : form
    }
    return render(request, 'production/sn_tracking.html',context)

def unit_parameter_data(request,key):
    # form = snTrackingForm(request.POST or None ,initial={'sn': sn})
    # queryset=None
    # if form.is_valid():
    #     sn = form.cleaned_data["sn"]
    #         #print (sn)
    print ('Parameter Details')
    queryset=PerformingDetails.objects.filter(performing__pk=key)

    data ={
        "sn" : queryset[0].performing.sn_wo.sn,
        "workorder" : queryset[0].performing.sn_wo.workorder,
        "title" : "Parameter Data",
        "queryset" : queryset
    }
    context ={
        "data": data,
    }
    return render(request, 'production/parameter_tracking.html',context)


#SN tracking - Parameter
#def unit_tracking_parameter(request,sn,station):

def graph_histogram_by_range(request,family,station,parameter,date_range ='7day'):
    import datetime
    from datetime import date

    if date_range=='6week':
        default_start = date.today()  - datetime.timedelta(days=42)
        date_to = datetime.datetime.strftime(date.today()+datetime.timedelta(days=1),"%Y-%m-%d")
        group_by='week'
    elif date_range=='14day':
        default_start = date.today()  - datetime.timedelta(days=14)
        date_to = datetime.datetime.strftime(date.today()+datetime.timedelta(days=1),"%Y-%m-%d")
        group_by='date'
    elif date_range=='4month':
        default_start = date.today()  - relativedelta(months=4)
        date_to = datetime.datetime.strftime(date.today()+ relativedelta(months=1),"%Y-%m-%d")
        group_by='month'
    else: #7days
        default_start = date.today()  - datetime.timedelta(days=7)
        date_to = datetime.datetime.strftime(date.today()+datetime.timedelta(days=1),"%Y-%m-%d")
        group_by='date'

    date_from= datetime.datetime.strftime(default_start,"%Y-%m-%d")
    

    print ('Histogram by Range from %s to %s' % (date_from,date_to))

    return graph_histogram(request,family,station,date_from,date_to,parameter)

def graph_histogram(request,family,station,
                          date_from,date_to,parameter):
    import numpy as np
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt
    

    #Query data
    import datetime
    from django.db.models import Count,Max,Min,Avg,StdDev
    date_from = datetime.datetime.strptime(date_from,'%Y-%m-%d')
    date_to = datetime.datetime.strptime(date_to,'%Y-%m-%d')

    from django.utils import timezone
    # current_tz = timezone.get_current_timezone()
    # date_from=current_tz.localize(date_from )
    # date_to =current_tz.localize (date_to )
    print ('Graph distribution input data : %s %s %s %s %s' % (family,station,date_from,date_to,parameter))
    #replace  -slash- with /
    parameter=parameter.replace('-slash-','/')

    from django.db.models import F
    # pt = PerformingDetails.objects.filter(
    #     performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
    #     performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
    #     parameter__name=parameter,
    #     performing__sn_wo__workorder__product__family__name=family,
    #     performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min'))
    

    # pt = PerformingDetails.objects.filter(
    #     performing__started_date__range=[date_from,date_to],
    #     parameter__name=parameter,
    #     performing__sn_wo__workorder__product__family__name=family,
    #     performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min'))
    pt = PerformingDetails.objects.filter(
        performing__started_date__range=[date_from,date_to],
        parameter__name=parameter,
        performing__sn_wo__workorder__product__family__name=family,
        performing__station__station=station).exclude(value = None)


    if pt.count()==0:
        print ('No data %s %s %s %s %s' % (family,station,date_from,date_to,parameter))
        return HttpResponse("Not Found Data")


    #get Aggregate data
    means = pt.aggregate(mean=Avg('value')).get('mean')
    stddev = pt.aggregate(stddev=StdDev('value')).get('stddev')

    max_value  = pt.aggregate(max=Max('value')).get('max')
    min_value  = pt.aggregate(min=Min('value')).get('min')

    x = pt.values_list('value', flat=True)

    limit_min = pt.aggregate(min=Max('limit_min')).get('min')
    limit_max = pt.aggregate(max=Min('limit_max')).get('max')

    # F = gcf()
    # Size = F.get_size_inches()
    # fig = plt.Figure(figsize=(15,8))
    fig = plt.Figure(figsize=(15,8))
    fig.patch.set_facecolor('white')

    ax = fig.add_subplot(111) #211 ,111
   
    # example data
    mu = means #100  # mean of distribution
    sigma = stddev #15  # standard deviation of distribution
    #x = mu + sigma * np.random.randn(10000)
    import math
    #num_bins = 20 if pt.count()>100 else pt.count()
    num_bins =math.ceil(((max_value-min_value)/stddev))*2

    # the histogram of the data
    
    #print ('Min : %s , Max: %s  , def: %s , num : %s' % (min_value,max_value,max_value-min_value,num_bins))
    n, bins, patches = ax.hist(x, num_bins, normed=1, facecolor='green', alpha=0.7)
    #binwidth=1.0
    #n, bins, patches = ax.hist(x, np.arange(min(x), max(x) + binwidth, binwidth), normed=1, facecolor='green', alpha=0.7)
    #print (bins)
    # add a 'best fit' line
    # print (x.count())
    # print (n)
    # print (bins)

    y = mlab.normpdf(bins, mu, sigma)

    #ax.plot(x,cl,linestyle='-',color='black', linewidth=2)

    #ax.set_xlim(limit_min,limit_max)

    ax.plot(bins, y, 'r--')
    #ax.set_xlabel('%s on %s' % (parameter,tester))
    #Cp/Cpk
    Cp = (limit_max-limit_min)/(6*sigma)
    Cpl = (means-limit_min)/(3*sigma)
    Cpu = (limit_max-means)/(3*sigma)
    Cpk = Cpl if Cpl < Cpu else Cpl
    ax.set_ylabel('Probability')
    ax.set_title(r'Histogram of %s : $\mu = %0.2f $, $\sigma=%0.2f$' % (parameter,means,stddev))
    #ax.set_xlabel('Cp: %0.2f  / Cpk: %0.2f' % (Cp,Cpk))

    # draw a default vline at x=1 that spans the yrange
    l = ax.axvline(x=limit_min)
    ax.text(limit_min,max(y),('LSL=%s' % limit_min), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

    l = ax.axvline(x=limit_max)
    ax.text(limit_max,max(y),('USL=%s' % limit_max), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

    ax.set_xlim([limit_min-(3*sigma),limit_max+(3*sigma)])

    #fig.set_size_inches(13,8, forward=True)
    fig.tight_layout()
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def graph_distribution_by_range(request,family,station,parameter,date_range ='7day'):
    import datetime
    from datetime import date

    if date_range=='6week':
        default_start = date.today()  - datetime.timedelta(days=42)
        date_to = datetime.datetime.strftime(date.today()+datetime.timedelta(days=1),"%Y-%m-%d")
        group_by='week'
    elif date_range=='14day':
        default_start = date.today()  - datetime.timedelta(days=14)
        date_to = datetime.datetime.strftime(date.today()+datetime.timedelta(days=1),"%Y-%m-%d")
        group_by='date'
    elif date_range=='4month':
        default_start = date.today()  - relativedelta(months=4)
        date_to = datetime.datetime.strftime(date.today()+ relativedelta(months=1),"%Y-%m-%d")
        group_by='month'
    else: #7days
        default_start = date.today()  - datetime.timedelta(days=7)
        date_to = datetime.datetime.strftime(date.today()+datetime.timedelta(days=1),"%Y-%m-%d")
        group_by='date'

    date_from= datetime.datetime.strftime(default_start,"%Y-%m-%d")
    

    print ('Distribution by Range from %s to %s' % (date_from,date_to))

    return graph_distribution(request,family,station,date_from,date_to,parameter)


def graph_distribution(request,family,station,
                          date_from,date_to,parameter):
    import numpy as np
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt
    

    #Query data
    import datetime
    from django.db.models import Count,Max,Min,Avg,StdDev
    date_from = datetime.datetime.strptime(date_from,'%Y-%m-%d')
    date_to = datetime.datetime.strptime(date_to,'%Y-%m-%d')

    from django.utils import timezone
    # current_tz = timezone.get_current_timezone()
    # date_from=current_tz.localize(date_from )
    # date_to =current_tz.localize (date_to )
    print ('Graph distribution input data : %s %s %s %s %s' % (family,station,date_from,date_to,parameter))
    #replace  -slash- with /
    parameter=parameter.replace('-slash-','/')

    from django.db.models import F
    # pt = PerformingDetails.objects.filter(
    #     performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
    #     performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
    #     parameter__name=parameter,
    #     performing__sn_wo__workorder__product__family__name=family,
    #     performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min'))
    

    # pt = PerformingDetails.objects.filter(
    #     performing__started_date__range=[date_from,date_to],
    #     parameter__name=parameter,
    #     performing__sn_wo__workorder__product__family__name=family,
    #     performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min'))
    pt = PerformingDetails.objects.filter(
        performing__started_date__range=[date_from,date_to],
        parameter__name=parameter,
        performing__sn_wo__workorder__product__family__name=family,
        performing__station__station=station).exclude(value = None)


    if pt.count()==0:
        print ('No data %s %s %s %s %s' % (family,station,date_from,date_to,parameter))
        return HttpResponse("Not Found Data")


    #get Aggregate data
    means = pt.aggregate(mean=Avg('value')).get('mean')
    stddev = pt.aggregate(stddev=StdDev('value')).get('stddev')

    max_value  = pt.aggregate(max=Max('value')).get('max')
    min_value  = pt.aggregate(min=Min('value')).get('min')

    x = pt.values_list('value', flat=True)

    limit_min = pt.aggregate(min=Max('limit_min')).get('min')
    limit_max = pt.aggregate(max=Min('limit_max')).get('max')

    # F = gcf()
    # Size = F.get_size_inches()
    fig = plt.Figure(figsize=(15,8))
    fig.patch.set_facecolor('white')
    # fig.suptitle('Distribution data for %s (%s - %s)' % (parameter,family,station),fontsize=18)
    #fig.subplots_adjust(top=2)
    #fig.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')


    ax = fig.add_subplot(321) #211 ,111
    ay = fig.add_subplot(322)

    
    # example data
    mu = means #100  # mean of distribution
    sigma = stddev #15  # standard deviation of distribution
    #x = mu + sigma * np.random.randn(10000)
    import math
    #num_bins = 20 if pt.count()>100 else pt.count()
    num_bins =math.ceil(((max_value-min_value)/stddev))*2

    # the histogram of the data
    

    #print ('Min : %s , Max: %s  , def: %s , num : %s' % (min_value,max_value,max_value-min_value,num_bins))
    n, bins, patches = ax.hist(x, num_bins, normed=1, facecolor='green', alpha=0.7)
    #binwidth=1.0
    #n, bins, patches = ax.hist(x, np.arange(min(x), max(x) + binwidth, binwidth), normed=1, facecolor='green', alpha=0.7)
    #print (bins)
    # add a 'best fit' line
    # print (x.count())
    # print (n)
    # print (bins)

    y = mlab.normpdf(bins, mu, sigma)

    #ax.plot(x,cl,linestyle='-',color='black', linewidth=2)

    #ax.set_xlim(limit_min,limit_max)

    ax.plot(bins, y, 'r--')
    #ax.set_xlabel('%s on %s' % (parameter,tester))
    #Cp/Cpk
    Cp = (limit_max-limit_min)/(6*sigma)
    Cpl = (means-limit_min)/(3*sigma)
    Cpu = (limit_max-means)/(3*sigma)
    Cpk = Cpl if Cpl < Cpu else Cpl
    ax.set_ylabel('Probability')
    ax.set_title(r'Histogram of %s : $\mu = %0.2f $, $\sigma=%0.2f$' % (parameter,means,stddev))
    #ax.set_xlabel('Cp: %0.2f  / Cpk: %0.2f' % (Cp,Cpk))

    #Line for 
    # l = ax.axvline(x=means+(3*sigma))
    # l = ax.axvline(x=means-(3*sigma))
    # l = ax.axvline(x=means)
    # Tweak spacing to prevent clipping of ylabel
    #plt.subplots_adjust(left=0.15)
    #ax.set_subplots_adjust(left=0.15)
    #fig.set_size_inches(13,8, forward=True)

    #Line limit min/max
    # draw a default vline at x=1 that spans the yrange
    l = ax.axvline(x=limit_min)
    ax.text(limit_min,max(y),('LSL=%s' % limit_min), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

    l = ax.axvline(x=limit_max)
    ax.text(limit_max,max(y),('USL=%s' % limit_max), ha='left',
            verticalalignment='bottom',color='black', wrap=True,
            bbox={'facecolor':'red', 'alpha':0.5, 'pad':1})

    ax.set_xlim([limit_min-(3*sigma),limit_max+(3*sigma)])

    #Overall Box Plot
    #box_plot(ay,x,means,'Overall')



    
    ay.set_xlim([limit_min-(3*sigma),limit_max+(3*sigma)])
    
    #Box Plot by Tester
    tester_labels = pt.distinct('performing__tester').values_list('performing__tester',flat=True)
    user_labels = pt.distinct('performing__user').values_list('performing__user',flat=True)
    product_labels = pt.distinct('performing__sn_wo__workorder__product__name').values_list('performing__sn_wo__workorder__product__name',flat=True)

    tester_x_data=[]
    for tester in pt.distinct('performing__tester').values_list('performing__tester',flat=True):
        mylist = list(pt.filter(performing__tester=tester).values_list('value',flat=True))
        mylist.remove(max(mylist))
        tester_x_data.append(mylist)

    user_x_data=[]
    for user in pt.distinct('performing__user').values_list('performing__user',flat=True):
        mylist = list(pt.filter(performing__user=user).values_list('value',flat=True))
        mylist.remove(max(mylist))
        user_x_data.append(mylist)

    product_x_data=[]
    for product in pt.distinct('performing__sn_wo__workorder__product').values_list('performing__sn_wo__workorder__product',flat=True):
        mylist = list(pt.filter(performing__sn_wo__workorder__product=product).values_list('value',flat=True))
        mylist.remove(max(mylist))
        product_x_data.append(mylist)

    import numpy as np
    az = fig.add_subplot(323) #211 ,111
    az_dict=az.boxplot(tester_x_data,labels=tester_labels,showmeans=True)#rs
    az.set_xticklabels( tester_labels, rotation=0,ha='center')
    az.axhline(y=means,color='g' ,ls='dashed')
    az.set_title('By Tester')

        #Put Text on Graph

    # for line in az_dict['medians']:
    #     # get position data for median line
    #     x, y = line.get_xydata()[1] # top of median line
    #     # overlay median value
    #     if not np.isnan(y):
    #         az.text(x, y, '%.2f' % y,
    #         verticalalignment='bottom',ha='right',fontsize=14) # draw above, centered

    #ax.set_title(r'Parameter : %s' % (parameter))
    #az.set_xlabel('by Tester')


    ak = fig.add_subplot(325) #211 ,111
    ak.boxplot(user_x_data,labels=user_labels,showmeans=True)#rs
    ak.set_xticklabels( user_labels, rotation=0,ha='center')
    #ax.set_title(r'Parameter : %s' % (parameter))
    ak.axhline(y=means,color='g' ,ls='dashed')
    ak.set_title('by Operator')


    al = fig.add_subplot(324) #211 ,111
    al.boxplot(product_x_data,labels=product_labels,showmeans=True)#rs
    al.set_xticklabels( product_labels, rotation=0,ha='center')
    #ax.set_title(r'Parameter : %s' % (parameter))
    al.axhline(y=means,color='g' ,ls='dashed')
    al.set_title('by Product')



    from matplotlib.dates import DateFormatter
    import matplotlib.dates as dates
    plt.gcf().autofmt_xdate()

    ab = plt.gca()
    ab = fig.add_subplot(322)
    #a = np.linspace(1, x.count(), x.count(), endpoint=False)
    a= pt.values_list('performing__started_date',flat=True)
    ab.scatter(a, x)
    ab.set_ylim([limit_min,limit_max])
    ab.set_xlim([date_from,date_to])
    # ab.set_xtick( range(2004,2017,3),[str(i) for i in range(2004,2017,3)])
    #ab.set_xticklabels( a,rotation=40,ha='right')

    
    xab = ab.get_xaxis()

    if (date_to-date_from).days >60:
        xab.set_major_locator(dates.MonthLocator())
        xab.set_major_formatter(dates.DateFormatter('%b'))
        xab.set_minor_locator(dates.DayLocator(bymonthday=range(1,32)))
    else:
        xab.set_major_locator(dates.DayLocator())
        xab.set_major_formatter(dates.DateFormatter('%d'))
        xab.set_minor_locator(dates.HourLocator(byhour=range(0,24,3)))
        # xab.set_minor_formatter(dates.DateFormatter('%H'))
        #%Y-%m-%d

    xab.set_tick_params(which='major', pad=15,direction=0)
    # ab.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

    ab.axhline(y=means,color='g' ,ls='dashed')
    ab.set_title('Scatter Diagram')
    plt.setp( xab.get_majorticklabels(), rotation=0, horizontalalignment='center' )




    #fig.set_size_inches(13,8, forward=True)
    fig.tight_layout()
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def graph_boxplot(request,family,station,
                          date_from,date_to,parameter):
    import numpy as np
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt


    #Query data
    import datetime
    from django.db.models import Count,Max,Min,Avg,StdDev
    date_from = datetime.datetime.strptime(date_from,'%Y-%m-%d')
    date_to = datetime.datetime.strptime(date_to,'%Y-%m-%d')

    parameter=parameter.replace('-slash-','/')

    from django.db.models import F
    pt = PerformingDetails.objects.filter(
        performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
        performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
        parameter__name=parameter,
        performing__sn_wo__workorder__product__family__name=family,
        performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min'))

    means = pt.aggregate(mean=Avg('value')).get('mean')

    user_labels = pt.distinct('performing__user').values_list('performing__user',flat=True)
    user_x_data=[]
    for user in pt.distinct('performing__user').values_list('performing__user',flat=True):
        mylist = list(pt.filter(performing__user=user).values_list('value',flat=True))
        mylist.remove(max(mylist))
        user_x_data.append(mylist)

    adjustprops = dict(left=0.1, bottom=0.1, right=0.97, top=0.93, wspace=1, hspace=1)

    fig = plt.Figure()
    #fig.suptitle('Box plot of %s  (all tester)' % parameter , fontsize=14, fontweight='bold')
    fig.subplots_adjust(**adjustprops)
    


    ax = fig.add_subplot(111) #211 ,111
    ax.boxplot(user_x_data,labels=user_labels)#rs
    ax.set_xticklabels( user_labels, rotation=80,ha='right')
    #ax.set_title(r'Parameter : %s' % (parameter))
    ax.axhline(y=means,color='g' ,ls='dashed')
    ax.set_title(parameter)


    # ax.boxplot(x_data,labels=labels)#rs
    # ax.set_xticklabels( labels, rotation=80,ha='right')
    # #ax.set_title(r'Parameter : %s' % (parameter))
    # ax.set_xlabel('model: %s  / operation: %s' % (model_name,operation_name))
    #fig.set_size_inches(13,8, forward=True)
    fig.tight_layout()
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def test(request,family,station,parameter,date_range ='7day',by='date'):
    if request.method == 'GET':
        print ('GET......')
        return HttpResponse('GET methode')
    elif request.method == 'POST':
        param = request.POST.get("q", "")
        print ('POST......'+param)
        return HttpResponse('POST methode param =' +param)

def graph_relations(request,family,station,parameter,date_range ='7day',groupby='date'):
    import datetime
    from datetime import date

    if date_range=='6week':
        default_start = date.today()  - datetime.timedelta(days=42)
        group_by='week'
    elif date_range=='14day':
        default_start = date.today()  - datetime.timedelta(days=14)
        group_by='date'
    elif date_range=='4month':
        default_start = date.today()  - datetime.timedelta(days=120)
        group_by='month'
    else: #7days
        default_start = date.today()  - datetime.timedelta(days=7)
        group_by='date'

    start_date= datetime.datetime.strftime(default_start,"%Y-%m-%d")
    stop_date = datetime.datetime.strftime(date.today(),"%Y-%m-%d")

    if groupby != 'date':
        group_by = groupby

    print ('Range and Group from %s to %s' % (start_date,stop_date))

    data={
        "title":"Relation Paremeter Data",
        "family" : family,
        "station" : station,
        "parameter" :parameter,
        "date_range" : date_range,
        "date_from_str":start_date,
        "date_to_str":stop_date,
        "date_from":start_date,
        "date_to":stop_date,
        }
    print (station)
    context ={
        "data": data,
        }
    return render(request, 'production/spc_relations.html',context)
    # return graph_boxplot_by_date(request,family,station,date_from,date_to,parameter,group_by)

def graph_boxplot_by_range_group_value(request,family,station,parameter,date_range ='7day',groupby='date',value=''):
    import datetime
    from datetime import date

    if date_range=='6week':
        default_start = date.today()  - datetime.timedelta(days=42)
        group_by='week'
    elif date_range=='14day':
        default_start = date.today()  - datetime.timedelta(days=14)
        group_by='date'
    elif date_range=='4month':
        default_start = date.today()  - datetime.timedelta(days=120)
        group_by='month'
    else: #7days
        default_start = date.today()  - datetime.timedelta(days=7)
        group_by='date'

    date_from= datetime.datetime.strftime(default_start,"%Y-%m-%d")
    date_to = datetime.datetime.strftime(date.today(),"%Y-%m-%d")

    if groupby != 'date':
        group_by = groupby

    print ('Range ,Group and Value from %s to %s' % (date_from,date_to))

    return graph_boxplot_by_date(request,family,station,date_from,date_to,parameter,group_by)

def graph_boxplot_by_range_group(request,family,station,parameter,date_range ='7day',groupby='date'):
    import datetime
    from datetime import date

    if date_range=='6week':
        default_start = date.today()  - datetime.timedelta(days=42)
        group_by='week'
    elif date_range=='14day':
        default_start = date.today()  - datetime.timedelta(days=14)
        group_by='date'
    elif date_range=='4month':
        default_start = date.today()  - datetime.timedelta(days=120)
        group_by='month'
    else: #7days
        default_start = date.today()  - datetime.timedelta(days=7)
        group_by='date'

    date_from= datetime.datetime.strftime(default_start,"%Y-%m-%d")
    date_to = datetime.datetime.strftime(date.today(),"%Y-%m-%d")

    if groupby != 'date':
        group_by = groupby

    print ('Range and Group from %s to %s' % (date_from,date_to))

    return graph_boxplot_by_date(request,family,station,date_from,date_to,parameter,group_by)

def graph_boxplot_by_range(request,family,station,parameter,date_range ='7day'):
    import datetime
    from datetime import date

    if date_range=='6week':
        default_start = date.today()  - datetime.timedelta(days=42)
        group_by='week'
    elif date_range=='14day':
        default_start = date.today()  - datetime.timedelta(days=14)
        group_by='date'
    elif date_range=='4month':
        default_start = date.today()  - datetime.timedelta(days=120)
        group_by='month'
    else: #7days
        default_start = date.today()  - datetime.timedelta(days=7)
        group_by='date'

    date_from= datetime.datetime.strftime(default_start,"%Y-%m-%d")
    date_to = datetime.datetime.strftime(date.today(),"%Y-%m-%d")

    print ('from %s to %s' % (date_from,date_to))

    return graph_boxplot_by_date(request,family,station,date_from,date_to,parameter,group_by)

def graph_boxplot_by_date(request,family,station,
                          date_from,date_to,parameter,date_range='date',value=None):
    # import numpy as np
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt


    #Query data
    import datetime
    from django.db.models import Count,Max,Min,Avg,StdDev
    date_to_str=date_to
    date_from_str=date_from
    date_from = datetime.datetime.strptime(date_from,'%Y-%m-%d')
    date_to = datetime.datetime.strptime(date_to,'%Y-%m-%d') + datetime.timedelta(days=1)

    parameter=parameter.replace('-slash-','/')

    from django.db.models import F
    # pt = PerformingDetails.objects.filter(
    #     performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
    #     performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
    #     parameter__name=parameter,
    #     performing__sn_wo__workorder__product__family__name=family,
    #     performing__station__station=station,value__lt=F('limit_max'),value__gt=F('limit_min'))
    #Some parameter don't has Min or Max limit
    pt = PerformingDetails.objects.filter(
        performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
        performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
        parameter__name=parameter,
        performing__sn_wo__workorder__product__family__name=family,
        performing__station__station=station).exclude(value = None)

    adjustprops = dict(left=0.1, bottom=0.1, right=0.97, top=0.93, wspace=1, hspace=1)
    if pt.count()>0:
        station_name=pt[0].performing.station.name
        param_desc=pt[0].parameter.description
        total_sample=pt.count()
    else:
        station_name=station
        param_desc=parameter
        total_sample=0

    means = pt.aggregate(mean=Avg('value')).get('mean')
    print ('Total = %s , means = %s' %(pt.count(),means))

    if date_range=='date':
        delta = date_to - date_from
        date_labels = [date_from.strftime('%d')]
        date_serise = [date_from.strftime('%Y-%m-%d')]
        for i in range(1,delta.days):
            date_labels.append((date_from + datetime.timedelta(days=i)).strftime('%d'))
            date_serise.append((date_from + datetime.timedelta(days=i)).strftime('%Y-%m-%d'))
        date_x_data=[]

        for d in date_serise:
            date_obj_start=datetime.datetime.strptime(d,'%Y-%m-%d')
            date_obj_end =  date_obj_start + datetime.timedelta(days=1)
            # mylist = list(pt.filter(
            #     performing__started_date__gt=datetime.datetime(date_obj_start.year,date_obj_start.month,date_obj_start.day)
            #     ).values_list('value',flat=True))
            mylist = list(pt.filter(
                performing__started_date__gt=datetime.datetime(date_obj_start.year,date_obj_start.month,date_obj_start.day),
                performing__started_date__lt=datetime.datetime(date_obj_end.year,date_obj_end.month,date_obj_end.day)
                ).values_list('value',flat=True))
            date_x_data.append(mylist)
    elif date_range=='week':
        last_week_number=6
        date_to = datetime.datetime.strptime(date_to_str,'%Y-%m-%d') #Not last day of week
        (begin_of_week,end_of_week)=week_magic (date_to) #Get last day of week.
        date_from = end_of_week - datetime.timedelta(days=last_week_number*7)
        (current_year,current_week,day_of_week)=date_to.isocalendar()
        
        delta= last_week_number
        date_labels = [date_from.strftime('W%W')]
        date_serise = [date_from.strftime('%Y-W%W')]
        for i in range(1,delta):
            date_labels.append((date_from + datetime.timedelta(days=i*7)).strftime('W%W'))
            date_serise.append((date_from + datetime.timedelta(days=i*7)).strftime('%Y-W%W'))
        date_x_data=[]
        
        for d in date_serise:
            date_obj_start = datetime.datetime.strptime(d + '-0', "%Y-W%W-%w")
            date_obj_end =  date_obj_start + datetime.timedelta(days=7)
            # mylist = list(pt.filter(
            #     performing__started_date__gt=datetime.datetime(date_obj_start.year,date_obj_start.month,date_obj_start.day)
            #     ).values_list('value',flat=True))
            mylist = list(pt.filter(
                performing__started_date__gt=datetime.datetime(date_obj_start.year,date_obj_start.month,date_obj_start.day),
                performing__started_date__lt=datetime.datetime(date_obj_end.year,date_obj_end.month,date_obj_end.day)
                ).values_list('value',flat=True))
            date_x_data.append(mylist)
    elif date_range=='month':
        last_month_number=5
        last_week_number=20
        date_to = datetime.datetime.strptime(date_to_str,'%Y-%m-%d') #Not last day of week
        from dateutil.relativedelta import relativedelta
        (begin_of_to_week,end_of_to_week)=week_magic (date_to) #Get last day of week.
        (current_year,current_to_week,day_of_to_week)=date_to.isocalendar()

        date_from = end_of_to_week - relativedelta(months=last_month_number)
        (current_year,current_from_week,day_of_from_week)=date_from.isocalendar()

        delta= current_to_week-current_from_week
        date_labels = [date_from.strftime('W%W')]
        date_serise = [date_from.strftime('%Y-W%W')]

        for i in range(1,delta):
            if (i%4)==0:
                date_labels.append((date_from + datetime.timedelta(days=i*7)).strftime('W%W'))
            else:
                date_labels.append('')
            date_serise.append((date_from + datetime.timedelta(days=i*7)).strftime('%Y-W%W'))
        date_x_data=[]
        

        for d in date_serise:
            date_obj_start = datetime.datetime.strptime(d + '-0', "%Y-W%W-%w")
            date_obj_end =  date_obj_start + datetime.timedelta(days=7)
            mylist = list(pt.filter(
                performing__started_date__gt=datetime.datetime(date_obj_start.year,date_obj_start.month,date_obj_start.day)
                ).values_list('value',flat=True))
            date_x_data.append(mylist)

    elif date_range=='tester':
        
        if value == None :
            date_labels = pt.distinct('performing__tester').values_list('performing__tester',flat=True)
            date_x_data=[]
            for tester in pt.distinct('performing__tester').values_list('performing__tester',flat=True):
                mylist = list(pt.filter(performing__tester=tester).values_list('value',flat=True))
                # mylist.remove(max(mylist))
                date_x_data.append(mylist)
        else: #By Tester Slot -- attribute_code=5111
            date_labels = pt.distinct('performing__tester').values_list('performing__tester',flat=True)

    elif date_range=='part':
        date_labels = pt.distinct('performing__sn_wo__workorder__product__name').values_list('performing__sn_wo__workorder__product__name',flat=True)
        date_x_data=[]
        for product in pt.distinct('performing__sn_wo__workorder__product').values_list('performing__sn_wo__workorder__product',flat=True):
            mylist = list(pt.filter(performing__sn_wo__workorder__product=product).values_list('value',flat=True))
            date_x_data.append(mylist)
    
    elif date_range=='operator':
        date_labels =pt.distinct('performing__user__username').values_list('performing__user__username',flat=True)
        date_x_data=[]
        for user in pt.distinct('performing__user__username').values_list('performing__user__username',flat=True):
            mylist = list(pt.filter(performing__user__username=user).values_list('value',flat=True))
            date_x_data.append(mylist)

    elif date_range=='temperature':
        # Same Parameter ,Same Frequency and Same station
        cuttedParam=parameter.split('(')[0]
        filterParam = cuttedParam + '('
        currTemp= pt[0].parameter.attribute.temperature
        currFreq= pt[0].parameter.attribute.frequency
        
        # param_req=Parameter.objects.filter(name__contains=cuttedParam,attribute__frequency=currFreq,group=station)
        # # print (param_req)
        # date_labels =param_req.distinct('attribute__temperature').values_list('attribute__temperature',flat=True)
        # # print (date_labels)
        # snlist = pt.values_list('performing__sn_wo')#Sn list in Main operation

        snlist = pt.values_list('performing__sn_wo')#Sn list in Main operation
        param_req = PerformingDetails.objects.filter(
            performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
            performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
            parameter__name__contains=filterParam,
            performing__sn_wo__in=snlist,
            parameter__attribute__frequency=currFreq,
            performing__station__station=station).exclude(value = None)
        date_labels =param_req.distinct('parameter__attribute__temperature').values_list('parameter__attribute__temperature',flat=True)

        date_x_data=[]
        for p in date_labels:
            # print (p)
            mylist = list(param_req.filter(parameter__attribute__temperature=p).values_list('value',flat=True))
            date_x_data.append(mylist)

        param_desc= '%s (%s)' % (cuttedParam,currFreq)

    elif date_range=='frequency':
        # Same Parameter ,Same Frequency and Same station
        cuttedParam=parameter.split('(')[0] 
        filterParam = cuttedParam + '('
        currTemp= pt[0].parameter.attribute.temperature
        currFreq= pt[0].parameter.attribute.frequency
        print ('%s %s %s' % (filterParam,currTemp,currFreq))
        
        # param_req=Parameter.objects.filter(name__contains=filterParam,attribute__temperature=currTemp,group=station)
        
        # date_labels =param_req.distinct('attribute__frequency').values_list('attribute__frequency',flat=True)
        snlist = pt.values_list('performing__sn_wo')#Sn list in Main operation
        param_req = PerformingDetails.objects.filter(
            performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
            performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
            parameter__name__contains=filterParam,
            performing__sn_wo__in=snlist,
            parameter__attribute__temperature=currTemp,
            performing__station__station=station).exclude(value = None)
        date_labels =param_req.distinct('parameter__attribute__frequency').values_list('parameter__attribute__frequency',flat=True)

        # print (param_req)
        # print (date_labels)
        # return drawEmptyGraph(date_range,'Parameter %s does not exist in system' % date_range)
        
        # snlist_temp = PerformingDetails.objects.filter(performing__sn_wo__in =snlist,
        #             performing__station__station = station,parameter__in =param_req )
        date_x_data=[]
        new_date_labels=[]
        unitName='THz'
        for p in date_labels:
            # print (p)
            mylist = list(param_req.filter(parameter__attribute__frequency=p).values_list('value',flat=True))
            date_x_data.append(mylist)
            new_date_labels.append(p.replace(unitName,''))

        date_labels=new_date_labels #Value with

        param_desc= '%s (%s)' % (cuttedParam,currTemp)
        date_range = '%s (%s)' % (date_range,unitName)


        # return drawEmptyGraph(date_range,'Parameter %s  %s' % (cuttedParam,currTemp))

        # date_x_data=[]
        # for user in pt.distinct('performing__user__username').values_list('performing__user__username',flat=True):
        #     mylist = list(pt.filter(performing__user__username=user).values_list('value',flat=True))
        #     date_x_data.append(mylist)

    else : #Parameter Name
        #1)check Parameter exist in system
        param_req=Parameter.objects.filter(name=date_range)
        if param_req.count() ==0 :
            return drawEmptyGraph(date_range,'Parameter %s does not exist in system' % date_range)

        snlist = pt.values_list('performing__sn_wo')#Sn list in Main operation
        # newStationList=param_req.values_list('group')#station list of input parameter-->New Add

        #Check First Serial ,Is it same level
        pt_new=PerformingDetails.objects.filter(performing__sn_wo= pt.first().performing.sn_wo,
                        parameter__name=date_range) #list of target Parameter
       
        if pt_new.count()>0 : #Parameter in same Level
            print ('Start on query data on same Level of %s' % date_range)
            #get Station of parameter
            param_station=pt_new.first().performing.station
            #get parameter of all sn 
            pt_new=PerformingDetails.objects.filter(performing__sn_wo__in =snlist,
                        parameter__name=date_range,performing__station=param_station) #list of target Parameter

            date_labels=pt_new.distinct('value_str').values_list('value_str',flat=True)
            date_x_data=[]
            print ('Starting loop %s' % date_labels)
            for p in date_labels:
                print ('Querying loop %s' % p)
                snlist_parameter= PerformingDetails.objects.filter(performing__sn_wo__in =snlist,
                    parameter__name=date_range,performing__station=param_station,value_str=p).values_list('performing__sn_wo')

                mylist = list(pt.filter(performing__sn_wo__in=snlist_parameter).values_list('value',flat=True))
                date_x_data.append(mylist)
            if pt_new.count()>0 :
                date_range=pt_new[0].parameter.description
            print ('Finished')
        else: #either parameter not existing or in another Level.
            #1)get setting value of Product
            print ('Start on query data on another Level')
            from django.conf import settings
            param_setting = getattr(settings, "PCBA_SN", None)
            if param_setting == None:
                return drawEmptyGraph(date_range,'No PCBA Serial number attribute configuration')

            att_family =param_setting.get(family)
            if att_family == '':
                return drawEmptyGraph(date_range,'Not found PCBA Serial number configuration of %s' % family )
            #2)Get list for attribute of PIC Serial number
            param_list=[att_family[k] for k in att_family]

            # qs_parm=Parameter.objects.filter(name__in=param_list)
            # if qs_parm.count()>0:
            #     qs_pic= PerformingDetails.objects.filter(performing__sn_wo__in =snlist,
            #         parameter__name__in = param_list,performing__station=qs_parm)


            #3)Get list of PIC serial number from CFP level
            qs_pic= PerformingDetails.objects.filter(performing__sn_wo__in =snlist,
                    parameter__name__in = param_list)

            if qs_pic.count()==0:
                return drawEmptyGraph(date_range,'Not found data of parameter %s' % param_list)

            

            snlist_pic = qs_pic.values_list('value_str',flat=True)
            #3.1)Get Assembly Station
            assyStation=qs_pic.first().performing.station
            # print (qs_pic.count())
            #4)Get list data of PIC level (Pic SN + Pic Parameter)
            param_pic = date_range
            # print (snlist_pic)
            # print (param_pic)
            qs_pic_data = PerformingDetails.objects.filter(performing__sn_wo__sn__in = snlist_pic,
                    parameter__name=param_pic)
            #5)get PIC parameter value
            date_labels=qs_pic_data.distinct('value_str').values_list('value_str',flat=True)
            if len(date_labels)==0:
                return drawEmptyGraph(date_range,'Data of parameter is empty')


            date_x_data=[]

            # pt = PerformingDetails.objects.filter(
            #     performing__started_date__gt=datetime.datetime(date_from.year,date_from.month,date_from.day),
            #     performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
            #     parameter__name=parameter,
            #     performing__sn_wo__workorder__product__family__name=family).exclude(value = None)
            pt_assy = PerformingDetails.objects.filter(
                        performing__started_date__lt=datetime.datetime(date_to.year,date_to.month,date_to.day),
                        performing__station = assyStation,
                        performing__sn_wo__in = snlist).exclude(value = None)
            print ('Starting loop %s' % date_labels)
            for p in date_labels:
                print (p)
                #5.1)Get list of PIC sn that used p value
                qs_pic_used_p = qs_pic_data.filter(value_str=p)
                snlist_pic_used_p = qs_pic_used_p.values_list('performing__sn_wo__sn',flat=True)

                #5.2)Get CFP SN that param=XXXX and value_str=snlist_pic_used_p from CFP_List
                qs_snlist_cfp = pt_assy.filter(value_str__in =snlist_pic_used_p)
                sn_list_cfp = qs_snlist_cfp.values_list('performing__sn_wo',flat=True)
                mylist = list(pt.filter(performing__sn_wo__in=sn_list_cfp).values_list('value',flat=True))
                date_x_data.append(mylist)


                print (qs_pic_used_p.count())
                print (qs_snlist_cfp.count())
            if qs_pic_data.count()>0 :
                date_range= qs_pic_data[0].parameter.description + '  of ' + qs_pic_data[0].performing.sn_wo.workorder.product.family.name







    

    fig = plt.Figure()
    #fig.suptitle('Box plot of %s  (all tester)' % parameter , fontsize=14, fontweight='bold')
    fig.subplots_adjust(**adjustprops)
    fig.patch.set_facecolor('white')
    # plt.tick_params(axis='both', which='major', labelsize=24)
    # plt.tick_params(axis='both', which='minor', labelsize=18)

    ax = fig.add_subplot(111) #211 ,111
   
    bp_dict=ax.boxplot(date_x_data,labels=date_labels,showmeans=True,sym='')#remove filer (outlier)
    #date_x_data=reject_outliers(date_x_data)
    # bp_dict=ax.boxplot(date_x_data,labels=date_labels,showmeans=True)
    #,fontsize=18
    
    #ax.set_xticklabels( date_labels, rotation=0,ha='center')
    # ax.set_xticklabels(['%s\n$n$=%d'%(l, len(x)) for l, x in zip(date_labels,date_x_data)])
    tickFontSize=14
    ax.set_xticklabels(['%s\n $%d$'%(l, len(x)) for l, x in zip(date_labels,date_x_data)],fontsize=tickFontSize)
    zed = [tick.label.set_fontsize(tickFontSize) for tick in ax.yaxis.get_major_ticks()]
    zed = [tick.label.set_fontsize(tickFontSize) for tick in ax.xaxis.get_major_ticks()]

    if not means == None :
        ax.axhline(y=means,color='g' ,ls='dashed')
    

    # ax.set_title('%s  (%s : %s)' % (parameter,family,station_name),fontsize=16)
    ax.set_title('%s ($n$=%d)' % (param_desc,total_sample),fontsize=16)
    ax.set_xlabel('%s' % date_range)

    #Put Text on Graph
    import numpy as np
    ymin, ymax = ax.get_ylim()
    for line,sample in zip(bp_dict['medians'],date_x_data):
        # get position data for median line
        x, y = line.get_xydata()[1] # top of median line
        # overlay median value
        if not np.isnan(y):
            ax.text(x, y, '%.2f' % y,
            verticalalignment='bottom',ha='right',fontsize=12) # draw above, centered

            # ax.text(x, ymax-ymax*0.05, '$n$=%d' % len(sample),
            # verticalalignment='bottom',ha='right',fontsize=14) # draw above, centered
            
                
    #0 # bottom of left line
    #1 # bottom of right line
    #2 # top of right line
    #3 # top of left line

    for line,sample in zip(bp_dict['boxes'],date_x_data):
        x, y = line.get_xydata()[3] # bottom of left line
        if len(sample)>0:
            ax.text(x,y, '%.2f' % y,
                 horizontalalignment='left', # centered
                 verticalalignment='bottom',fontsize=8)      # below
            x, y = line.get_xydata()[0] # bottom of right line
            ax.text(x,y, '%.2f' % y,
                 horizontalalignment='left', # centered
                     verticalalignment='bottom',fontsize=8)      # below
    # fig.tight_layout()
    fig.set_tight_layout(True)
    canvas=FigureCanvas(fig )
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response

# def reject_outliers2(data, m=2):
#     import numpy as np
#     return data[abs(data - np.mean(data)) < m * np.std(data)] 

# def reject_outliers(data, m = 2.):
#     import numpy as np
#     d = np.abs(data - np.median(data))
#     mdev = np.median(d)
#     s = d/mdev if mdev else 0.
#     return data[s<m]

def drawEmptyGraph(date_range,message=None):
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import django
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt
    adjustprops = dict(left=0.1, bottom=0.1, right=0.97, top=0.93, wspace=1, hspace=1)
    param_desc=Parameter.objects.filter(name=date_range)
    left, width = .25, .5
    bottom, height = .25, .5
    right = left + width
    top = bottom + height
    fig = plt.Figure()
    fig.subplots_adjust(**adjustprops)
    fig.patch.set_facecolor('white')
    ax = fig.add_subplot(111) #211 ,111
    if param_desc.count()>0 :
        p_desc=param_desc[0].description
    else:
        p_desc=date_range
    str='Not found data of Parameter :\n %s' % p_desc
    if message :
        str= message     
    

    ax.text(0.5*(left+right), 0.5*(bottom+top), str,
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=20, color='red',
        transform=ax.transAxes)
    fig.tight_layout()
    canvas=FigureCanvas(fig )
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response



def box_plot(ax,data,means,title=''):
    #import numpy as np
    #np.random.seed(937)
    #data = np.random.lognormal(size=(37, 4), mean=1.5, sigma=1.75)
    #labels = list('ABCD')
    ax.boxplot(data, 0, 'gD', 0)#rs
    #(data, 0, 'rs', 0,meanline=True, showmeans=True)
    #ax.set_xlabel('x-label')
    #ax.set_ylabel('y-label')
    ax.axvline(x=means,color='g' ,ls='dashed')
    ax.set_title(title)



def reject_outliers(data):
    import numpy as np
    m = 2
    u = np.mean(data)
    s = np.std(data)
    filtered = [e for e in data if (u - 2 * s < e < u + 2 * s)]
    return filtered


def week_magic(day):
    import datetime
    day_of_week = day.weekday()

    to_beginning_of_week = datetime.timedelta(days=day_of_week)
    beginning_of_week = day - to_beginning_of_week

    to_end_of_week = datetime.timedelta(days=6 - day_of_week)
    end_of_week = day + to_end_of_week

    return (beginning_of_week, end_of_week)


def month_magic(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    from datetime import date, timedelta
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    first_day= date(y+a, m+1, 1)
    
    m=0
    y, m = dt.year + d_years, dt.month + m
    a, m = divmod(m-1, 12)
    last_day= date(y+a, m+1, 1) + timedelta(-1)
    return (first_day,last_day)