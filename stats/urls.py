from django.urls import path

from . import views

app_name = 'stats'
urlpatterns = [
    path('search/<username>/', views.lookup, name="username"),
    path('search/<username>/network', views.lookup),
    path('search/<username>/skywars', views.lookup),
    path('search/<username>/bedwars', views.lookup),
    path('search/', views.search),
]
