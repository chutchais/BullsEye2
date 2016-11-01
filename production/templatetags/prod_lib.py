from django import template

register = template.Library()

@register.filter
def to_slash(value):
    return value.replace("/","-slash-")


@register.assignment_tag
def percent(xin,xout):
	return 0 if (xin == 0 or xout==0) else (xout/xin)*100


@register.assignment_tag
def number_record(performing,family,station):
	return performing.filter(station__family=family,station__station=station).count()

@register.assignment_tag
def number_passed(performing,family,station):
	return performing.filter(station__family=family,station__station=station,result=True).count()


@register.filter
def in_family(stations, family):
    return stations.filter(family=family).order_by('ordering')

@register.filter
def critical_station(parameter, station):
    return parameter.filter(group=station,critical=True).order_by('ordering')

@register.filter
def annotate_parameter(performingdetails):
	from django.db.models import Count,Max,Min,Avg,StdDev
	return performingdetails.values('parameter__name').annotate(total=Count('value'))

@register.simple_tag(name='cpu')
def cpu(usl,avg,std):
    return 0 if std == 0 else (usl-avg)/(3*std)


@register.simple_tag(name='cpl')
def cpl(lsl,avg,std):
    return 0 if std == 0 else (avg-lsl)/(3*std)


@register.simple_tag(name='cpk')
def cpk(lsl,usl,avg,std):
    if std == 0:
        z= 0
    else:
        x = (avg-lsl)/(3*std)
        y = (usl-avg)/(3*std)
        z = x if x < y else y
    return z


@register.simple_tag(name='cp')
def cp(lsl,usl,std):
    if std == 0:
        y = 0
    else:
        y = (usl-lsl)/(6*std)
    return y