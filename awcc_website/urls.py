from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^auth/', 'customer_report.views.auth_and_login'),
    url(r'^login/', 'customer_report.views.loginview'),
    url(r'^logout/', 'customer_report.views.logout_view'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grouped_time/$', 'customer_report.views.grouped_time'), 
    url(r'^all_orders/$', 'customer_report.views.all_orders'), 
    url(r'^$', 'awcc_website.views.index'), 
)
