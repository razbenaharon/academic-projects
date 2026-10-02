from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('QueryResults', views.QueryResults, name='QueryResults'),
    path('AddTransaction', views.AddTransaction, name='AddTransaction'),
    path('BuyStocks', views.BuyStocks, name='BuyStocks')
]


