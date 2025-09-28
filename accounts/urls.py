from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .views import CustomLoginView

urlpatterns = [
    # ユーザー関連
    path('signup/', views.signup_view, name='signup'),
    path('profile_setup/', views.profile_setup_view, name='profile_setup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('mypage/', views.mypage_view, name='mypage'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/', redirect_field_name=None), name='logout'),

    # パスワードリセット関連
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # 役割ごとの専用ページ
    path("supporter/dashboard/", login_required(TemplateView.as_view(
        template_name="accounts/supporter_dashboard.html")), name="supporter_dashboard"),
    path("creator/dashboard/", login_required(TemplateView.as_view(
        template_name="accounts/creator_dashboard.html")), name="creator_dashboard"),
    path("craftsman/dashboard/", login_required(TemplateView.as_view(
        template_name="accounts/craftsman_dashboard.html")), name="craftsman_dashboard"),
    path('craftsman/register/', views.register_craftsman, name='register_craftsman'),
]