from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, ProfileForm
from .models import Profile
from django.contrib.auth.views import LoginView

# サインアップ用ビュー
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)  # POST データでフォームを作成
        if form.is_valid():  # バリデーションチェック
            user = form.save()  # ユーザー作成
            login(request, user)  # 作成後すぐにログインさせる
            return redirect('profile_setup')  # プロフィール設定ページへリダイレクト
    else:
        form = SignUpForm()  # GET の場合は空フォームを作成
    return render(request, 'accounts/signup.html', {'form': form})  # テンプレートにフォームを渡す

# プロフィール用ビュー
def profile_setup_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()

            # 役割ごとにリダイレクト先を変える
            if profile.role == 'supporter':
                return redirect('supporter_dashboard')
            elif profile.role == 'creator':
                return redirect('creator_dashboard')
            elif profile.role == 'craftsman':
                return redirect('craftsman_dashboard')

            return redirect('home')  # どの役割でもない場合のフォールバック
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_setup.html', {'form': form})

# ログイン用ビュー
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        role = self.request.user.profile.role  # Profile から role を取得
        if role == 'supporter':
            return '/accounts/supporter/dashboard/'
        elif role == 'creator':
            return '/accounts/creator/dashboard/'
        elif role == 'craftsman':
            return '/accounts/craftsman/dashboard/'
        return '/'

# マイページ用ビュー
def mypage_view(request):
    # ユーザーに紐づく Profile を取得
    profile = Profile.objects.get(user=request.user)
    # テンプレートに profile を渡す
    return render(request, 'accounts/mypage.html', {'profile': profile})
