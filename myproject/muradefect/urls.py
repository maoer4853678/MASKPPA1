from django.urls import path
from django.contrib import admin
from . import views


app_name = 'polls'
urlpatterns = [
    path('admin', admin.site.urls),
    
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    path("register", views.Register, name='register'),
    
    path('offset', views.Offset, name='offset'),
    path('ppa', views.Ppa, name='ppa'),
    path("alarm", views.Alarm, name='alarm'),
    path("data", views.Data, name='data'),
    path("option", views.Option, name='option'),
    
    
    path("getppa", views.GetPpa, name='getdata'),
    path("getoffset", views.GetOffset, name='getdata1'),
    path("getopsppa", views.GetOpsPpa, name='getdata1'),
    path("newset", views.NewSet, name='getdata1'),
    path("delset", views.DelSet, name='getdata1'),

]
