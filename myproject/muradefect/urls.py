from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
#    path('', views.index, name='index'),
#    path('/index', views.index, name='index'),
#    path('option', views.option, name='option'), ## 用户配置页面
#    path('plot', views.plot, name='plot'),
#    path('glasses', views.glasses_optimize, name='glasses_optimize'),
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
    path("getsumray", views.GetSumray, name='getdata1'),
    path("getopsppa", views.GetOpsPpa, name='getdata1'),

]
