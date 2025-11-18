from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),               # 一覧ページ
    path('<int:pk>/', views.project_detail, name='project_detail'),  # 詳細ページ
    path('<int:pk>/like/', views.toggle_like, name='toggle_like'),   # いいね
    path('<int:pk>/checkout/', views.create_checkout_session, name='checkout'),  # 支援
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/thanks/', views.thanks, name='thanks'),
    path('liked/', views.liked_projects, name='liked_projects'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
]
