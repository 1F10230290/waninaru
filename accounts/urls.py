from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('profile_setup/', views.profile_setup_view, name='profile_setup'),
    path('login/', views.login_view, name='login'),
    path('mypage/', views.mypage_view, name='mypage'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/', redirect_field_name=None), name='logout'),
]
