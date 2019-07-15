from django.urls import path
from django.contrib import admin
from . import views


app_name = 'muradefect'
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
    path("alarmrate", views.AlarmRate, name='alarm'),
    path("data", views.Data, name='data'),
    path("option", views.Option, name='option'),
    
    ## RestFul api
    path('log', views.LogEtl, name='log'),
    path('clear', views.Clear, name='clear'),
    path('setrateoption', views.SetRateOption, name='setrateoption'),
    path('download/<str:filename>', views.DownLoad, name='DownLoad'),
    path("getppa", views.GetPpa, name='getppa'),
    path("getoffset", views.GetOffset, name='getoffset'),
    path("downoffset", views.DownOffset, name='downoffset'),
    path("getopsppa", views.GetOpsPpa, name='getopsppa'),
    path("newset", views.NewSet, name='newset'),
    path("delset", views.DelSet, name='delset'),

]
