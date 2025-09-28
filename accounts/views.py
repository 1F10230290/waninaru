from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, ProfileForm, CraftsmanProfileForm
from .models import Profile, CraftsmanProfile
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
            return redirect('mypage')
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

# マイページ用
def mypage_view(request):
    profile = Profile.objects.get(user=request.user)

    craftsman_status = None
    craftsman_info = None  # 工芸士情報も渡す

    if profile.role == 'craftsman':
        try:
            craftsman_info = profile.craftsman_info
            craftsman_status = "工芸士登録済み" if craftsman_info.registered else "未登録"
        except CraftsmanProfile.DoesNotExist:
            craftsman_status = "未登録"

    return render(
        request,
        'accounts/mypage.html',
        {
            'profile': profile,
            'craftsman_status': craftsman_status,
            'craftsman_info': craftsman_info
        }
    )

# 工芸士情報登録
def register_craftsman(request):
    profile = request.user.profile

    # 既に CraftsmanProfile がある場合は取得、なければ新規作成
    craftsman_info, created = CraftsmanProfile.objects.get_or_create(profile=profile)

    if request.method == 'POST':
        form = CraftsmanProfileForm(request.POST, instance=craftsman_info)
        if form.is_valid():
            craftsman = form.save(commit=False)
            craftsman.registered = True  # 本登録にする
            craftsman.save()
            return redirect('mypage')  # マイページに戻る
    else:
        form = CraftsmanProfileForm(instance=craftsman_info)

    return render(request, 'accounts/register_craftsman.html', {'form': form})