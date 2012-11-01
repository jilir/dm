from django.conf.urls import patterns, include, url
from manager.views import success
from manager.views import upload_xml
from manager.views import statusback
from manager.views import create_project
from manager.views import find_free_machine
from manager.views import start_p
from manager.views import get_xml
from manager.views import get_task
from manager.views import upload_logs
from manager.views import show_status
from manager.views import show_hi
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	(r'^upload_xml/$', upload_xml),
	(r'^success/url/$', success),
	(r'^status/$', statusback),
	(r'^create_project/$',create_project),
	(r'^iamfree/$', find_free_machine),
	(r'^start/$', start_p),
	(r'^gettask/$', get_task),
	(r'^getxml/$', get_xml),
	(r'^upload_logs/$', upload_logs),
	(r'^show_status/$', show_status),
	(r'^hi/$', show_hi),
    # Examples:
    # url(r'^$', 'manager.views.home', name='home'),
    # url(r'^manager/', include('manager.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
