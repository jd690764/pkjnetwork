from django.conf.urls import url

from . import views

app_name = 'network'
urlpatterns = [
    url(r'^createNetwork/', views.createNetwork, name='createNetwork'),
    url(r'^display/', views.display, name='display'),
    url(r'^index/', views.index, name='index'),
    url(r'^lookup/', views.lookup, name='lookup'),
    #url(r'^lookupDisplay/', views.lookupDisplay, name='lookupDisplay'),
]
