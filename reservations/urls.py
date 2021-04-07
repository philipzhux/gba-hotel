from django.conf.urls import url
from . import views

urlpatterns = [url(r'^$', views.reservation, name='reservation'),
               url(r'^search/$', views.find_hotel, name='search'),
               url(r'^summary$', views.summary, name='summary'),
               url(r'^cancel$', views.cancel_reservation, name='cancel_reservation')]
