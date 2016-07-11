from django.conf.urls import url

from . import views

app_name = 'network'
urlpatterns = [
    url(r'^createNetwork/', views.createNetwork, name='createNetwork'),
    url(r'^display/', views.display, name='display'),
]
