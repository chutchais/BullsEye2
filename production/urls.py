from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^test/$', views.test, name='test'),
    url(r'^spc/cpk/(?P<family>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<date_range>[-\w|\W\ ]+)/', 
        views.spc_cpk_station, name='spc_cpk_station'),
    url(r'^spc/filter/get_family/', views.get_family, name='get_family'),
    url(r'^spc/filter/get_station/(?P<family>[-\w|\W\ ]+)/', views.get_station, name='get_station'),
    url(r'^spc/filter/get_product/(?P<family>[-\w|\W\ ]+)/', views.get_product, name='get_product'),
    url(r'^spc/filter/get_parameter/(?P<station>[-\w|\W\ ]+)/', views.get_parameter, name='get_parameter'),
    url(r'^spc/filter/', views.spc_filter, name='spc_filter'),
    url(r'^spc/(?P<family>[-\w|\W\ ]+)/', views.spc_main_graph, name='spc_main_family'),
    url(r'^spc/', views.spc_main_graph, name='spc_main_graph'),
    url(r'^graph/distribution/(?P<family>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/(?P<date_from>[-\w|\W\ ]+)/(?P<date_to>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/', 
        views.graph_distribution, name='graph_distribution'),
    url(r'^graph/distribution/(?P<family>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<date_range>[-\w|\W\ ]+)/', 
        views.graph_distribution_by_range, name='graph_distribution_by_range'),

    url(r'^graph/histogram/(?P<family>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<date_range>[-\w|\W\ ]+)/', 
        views.graph_histogram_by_range, name='graph_histogram_by_range'),

    url(r'^graph/boxplot/(?P<family>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/(?P<date_from>[-\w|\W\ ]+)/(?P<date_to>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<date_range>[-\w|\W\ ]+)/', 
        views.graph_boxplot_by_date, name='graph_boxplot_by_date'),
    url(r'^graph/boxplot/(?P<family>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<date_range>[-\w|\W\ ]+)/(?P<groupby>[-\w|\W\ ]+)/', 
        views.graph_boxplot_by_range_group, name='graph_boxplot_by_range_group'),
    url(r'^graph/boxplot/(?P<family>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<date_range>[-\w|\W\ ]+)/', 
        views.graph_boxplot_by_range, name='graph_boxplot_by_range'),

    url(r'^graph/relations/(?P<family>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<date_range>[-\w|\W\ ]+)/',
        views.graph_relations, name='graph_relations'),
    
    url(r'^station/(?P<station>[-\w|\W\ ]+)/(?P<family>[-\w|\W\ ]+)/$', views.get_process, name='get_process'),
    url(r'^station/$', views.post_list, name='post_list'),
    url(r'^bom/$', views.RecipeCreateView, name='RecipeCreateView'),
    url(r'^bomlist/$', views.getBOM, name='getBom'),
    url(r'^fits/upload/$', views.upload_fits, name='upload_fit'),
    url(r'^load/(?P<load_date>[-\w|\W\ ]+)/details/$', views.load_by_date, name='load_by_date'),
    url(r'^status/(?P<status>[-\w|\W\ ]+)/(?P<report_date>[-\w|\W\ ]+)/details/$', views.status_by_date, name='status_by_date'),
    url(r'^status/(?P<status>[-\w|\W\ ]+)/(?P<report_date>[-\w|\W\ ]+)/snlist/$', views.snlist_by_status_date, name='snlist_by_status_date'),
    url(r'^status/(?P<status>[-\w|\W\ ]+)/details/$', views.status_all, name='status_all'),
    url(r'^status/(?P<status>[-\w|\W\ ]+)/(?P<report_date>[-\w|\W\ ]+)/snlist/(?P<groupby>[-\w|\W\ ]+)/(?P<value>[-\w|\W\ ]+)$', 
        views.snlist_by_status_date_parameter, name='snlist_by_status_date_parameter'),
    url(r'^sn/parameter_data/(?P<key>[-\w|\W\ ]+)/$', views.unit_parameter_data, name='unit_parameter_data'),
    url(r'^sn/(?P<sn>[-\w|\W\ ]+)$', views.unit_tracking, name='unit_tracking'),
    url(r'^sn/$', views.unit_tracking ,{'sn': ''}, name='unit_tracking'),
    url(r'^wip/(?P<status>[-\w|\W\ ]+)/(?P<groupby>[-\w|\W\ ]+)/(?P<keyvalue>[-\w|\W\ ]+)/(?P<station>[-\w|\W\ ]+)/$',
        views.wip_serial, name='wip_serial'),
    url(r'^wip/(?P<status>[-\w|\W\ ]+)/(?P<groupby>[-\w|\W\ ]+)/(?P<value>[-\w|\W\ ]+)/$',
        views.wip_details, name='wip_details'),
    url(r'^wip/(?P<status>[-\w|\W\ ]+)/',views.wip_master, name='wip_master'),
]

