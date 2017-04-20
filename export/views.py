from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from io import StringIO,BytesIO

import pandas
from django_pandas.io import read_frame
from xlsxwriter.workbook import Workbook

# Create your views here.
# @api_view(['GET', 'POST'])
# def export_performing(request):
# 	print (request)
# 	family = request.GET.get('family','')
# 	station = request.GET.get('station','')
# 	date_from_in = request.GET.get('from','')
# 	date_to_in = request.GET.get('to','')


# 	import datetime
# 	from django.db.models import Count,Max,Min,Avg,StdDev

# 	date_from = datetime.datetime.strptime(date_from_in,'%Y-%m-%d')
# 	date_to = datetime.datetime.strptime(date_to_in,'%Y-%m-%d') + datetime.timedelta(days=1)

# 	kwargs={"performing__started_date__gt":datetime.datetime(date_from.year,date_from.month,date_from.day),
#             "performing__started_date__lt":datetime.datetime(date_to.year,date_to.month,date_to.day),
#             "performing__station__family__name":family,
#             "performing__station__station":station,
#             "parameter__spc_control":True}

# 	print ('%s -- %s -- %s --%s' % (family,station,date_from,date_to))

# 	# response = HttpResponse(content_type='application/vnd.ms-excel')
# 	# response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
	
# 	# Working Well
# 	response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
# 	response['Content-Disposition'] = 'attachment; filename=Report.xlsx'

# 	from production.models import PerformingDetails

# 	pd=PerformingDetails.objects.filter(**kwargs)
# 	# return HttpResponse('total records : %s' % pd.count())
# 	df=read_frame(pd,fieldnames=['performing__started_date','performing__sn_wo__sn',
# 		'performing__sn_wo__workorder__product','performing__tester','performing__slot','parameter__name','value'])

# 	dp = df.pivot_table(index=['performing__started_date','performing__sn_wo__sn','performing__sn_wo__workorder__product',
# 		'performing__tester','performing__slot'],columns='parameter__name')
    
# 	excel_file = BytesIO()
# 	xlwriter = pandas.ExcelWriter(excel_file, engine='xlsxwriter',options={'remove_timezone': True})
# 	dp.to_excel(xlwriter, 'sheetname')

# 	xlwriter.save()
# 	xlsx_data = excel_file.getvalue()
# 	excel_file.seek(0)
# 	response.write(xlsx_data)
# 	return response
def export_performing(request):
	# print (request)
	family = request.GET.get('family','')
	station = request.GET.get('station','')
	# date_from_in = request.GET.get('from','')
	# date_to_in = request.GET.get('to','')
	date_range = request.GET.get('range','')

	from datetime import date
	import datetime

	if date_range=='7day':
		default_start = date.today() - datetime.timedelta(days=7)
	elif date_range=='14day':
		default_start = date.today() - datetime.timedelta(days=14)
	elif date_range=='30day':
		default_start = date.today() - datetime.timedelta(days=30)
	elif date_range=='8week':
		default_start = date.today() - datetime.timedelta(days=56)
	elif date_range=='4month':
		default_start = date.today() - datetime.timedelta(months=4)
	else:
		default_start = date.today() - datetime.timedelta(days=7)

	date_from_in= datetime.datetime.strftime(default_start,"%Y-%m-%d")
	date_to_in = datetime.datetime.strftime(date.today(),"%Y-%m-%d")

	# print (start_date)
	# print (stop_date)
	# date_from_in = datetime.datetime.strptime(start_date,'%Y-%m-%d')
	# date_to_in = datetime.datetime.strptime(stop_date,'%Y-%m-%d')



	import datetime
	from django.db.models import Count,Max,Min,Avg,StdDev

	date_from = datetime.datetime.strptime(date_from_in,'%Y-%m-%d')
	date_to = datetime.datetime.strptime(date_to_in,'%Y-%m-%d') + datetime.timedelta(days=1)

	kwargs={"performing__started_date__gt":datetime.datetime(date_from.year,date_from.month,date_from.day),
            "performing__started_date__lt":datetime.datetime(date_to.year,date_to.month,date_to.day),
            "performing__station__family__name":family,
            "performing__station__station":station,
            "parameter__spc_control":True}

	print ('%s -- %s -- %s --%s' % (family,station,date_from,date_to))

	# response = HttpResponse(content_type='application/vnd.ms-excel')
	# response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
	
	# Working Well
	response = HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=Report.xlsx'

	from production.models import PerformingDetails

	pd=PerformingDetails.objects.filter(**kwargs)
	# return HttpResponse('total records : %s' % pd.count())
	df=read_frame(pd,fieldnames=['performing__started_date','performing__sn_wo__sn',
		'performing__sn_wo__workorder__product','performing__tester','performing__slot','parameter__name','value'])

	dp = df.pivot_table(index=['performing__started_date','performing__sn_wo__sn','performing__sn_wo__workorder__product',
		'performing__tester','performing__slot'],columns='parameter__name')
    
	excel_file = BytesIO()
	xlwriter = pandas.ExcelWriter(excel_file, engine='xlsxwriter',options={'remove_timezone': True})
	dp.to_excel(xlwriter, 'sheetname')

	xlwriter.save()
	xlsx_data = excel_file.getvalue()
	excel_file.seek(0)
	response.write(xlsx_data)
	return response

