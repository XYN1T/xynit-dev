from django.urls import path

from . import views

app_name = 'stats'
urlpatterns = [
    path('search/<username>/', views.lookup, name="username"),
    path('search/', views.search),
]
