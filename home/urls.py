from django.conf.urls import url
from . import views

urlpatterns = [url(r'^login/$', views.login, name='login'),
               url(r'^$', views.home, name='home'),
               url(r'^signup/$', views.signup, name='signup'),
               url(r'^logout/$', views.logout, name='logout'),
               url(r'^dashboard/$', views.dashboard, name='dashboard'),
               url(r'^profile/$', views.profile, name='profile'),
               url(r'^history/$', views.reservation_history, name='reservation_history')
               ]

