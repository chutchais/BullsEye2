"""shopfloor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls import include
from production import views
from django.views.generic.base import TemplateView
# from django.conf.urls.static import static
# from parameters import views
from ang.views import AngularTemplateView

urlpatterns = [
	# url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^production/', include('production.urls')),
    url(r'^dashboard/', include('production.urls')),
    url(r'^api/parameter/', include('parameters.api.urls')),
    url(r'^api/station/', include('stations.api.urls')),
    url(r'^api/tester/', include('tester.api.urls')),
    url(r'^api/family/', include('familys.api.urls')),
    url(r'^api/templates/(?P<item>[A-Za-z0-9\_\-\.\/]+)\.html$',  AngularTemplateView.as_view())
]

admin.site.site_header = 'Fabrinet - Administrator'

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns +=  [
    url(r'', TemplateView.as_view(template_name='ang/home.html'))
]