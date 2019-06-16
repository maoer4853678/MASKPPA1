from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
#    # ex: /polls/
#    path('',views.IndexView.as_view(), name='index'),
#    # ex: /polls/5/
#    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
#    # ex: /polls/5/results/
#    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#    # ex: /polls/5/vote/
#    path('<int:question_id>/vote/', views.vote, name='vote'),
#    
    path('', views.index, name='index'),
    path('option', views.option, name='option'), ## 用户配置页面
    path('plot', views.plot, name='plot'),
    path('glasses', views.glasses_optimize, name='glasses_optimize'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
]