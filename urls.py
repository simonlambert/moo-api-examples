from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'index.html', 'moo_api_examples.moo_oauth.views.index'),
    (r'^authorize', 'moo_api_examples.moo_oauth.views.authorize'),
    (r'^pack.json', 'moo_api_examples.moo_oauth.views.get_pack'),
)
