from django.conf.urls.defaults import patterns, include, url
import os
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sitebde.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')}),

    (r'^admin/?', include(admin.site.urls)),
    (r'^$', direct_to_template, {'template': 'rules.html'}),
    (r'^solve/$','probleme.views.submit'),
    (r'^dashboard/$','probleme.views.dashboard'),
    (r'^accounts/profile/$', direct_to_template, {'template': 'rules.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
)

urlpatterns += patterns('',url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),)
