from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    #''は空パス(/)にアクセスしたらindexビューを呼ぶ。名前を付けると{% url 'index%}と参照できるようになる。
    path('', views.index, name='index'),
    path('design/', views.design, name='design'), 
    path('generate/', views.generate, name='generate'), 
]
