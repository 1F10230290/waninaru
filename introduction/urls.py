from django.urls import path
from . import views

urlpatterns = [
    #''は空パス(/)にアクセスしたらindexビューを呼ぶ。名前を付けると{% url 'index%}と参照できるようになる。
    path('', views.index, name='index'),
]
