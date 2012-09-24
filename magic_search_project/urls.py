from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

from cards.search_indexes import CardIndex

sqs = SearchQuerySet()
for field_name in [name for name, field in CardIndex.fields.items() if field.faceted]:
    sqs = sqs.facet(field_name)

urlpatterns = patterns('',
    url(r'^$', FacetedSearchView(form_class=FacetedSearchForm, searchqueryset=sqs), name='haystack_search'),
    # Examples:
    # url(r'^$', 'magic_search_project.views.home', name='home'),
    # url(r'^magic_search_project/', include('magic_search_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
