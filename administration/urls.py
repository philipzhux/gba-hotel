from django.conf.urls import url
from . import views

urlpatterns = [url(r'^login/$', views.admin_login, name='admin_login'),
                url(r'^$', views.admin_login, name='admin_login'),
               url(r'^signup/$', views.admin_signup, name='admin_signup'),
               url(r'^logout/$', views.office_logout, name='office_logout'),
               url(r'^create/$', views.create_employee, name='create_employee'),
               url(r'^update/$', views.update_employee, name='update_employee'),
               url(r'^admin/$', views.admin, name='admin'),
               url(r'^service/$', views.employee, name='employee'),
               url(r'^profile/$', views.employee_profile, name='employee_profile'),
               url(r'^cancel/$', views.cancel_records, name='cancel_records'),
               url(r'^history$', views.reservation_records, name='reservation_records'),
]
