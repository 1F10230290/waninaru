from django.shortcuts import render, redirect
from django.contrib.auth import login
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

def craftsman_list_view(request):
    # role が 'craftsman' のユーザーのみ取得
    craftsmen = Profile.objects.filter(role='craftsman')
    return render(request, 'accounts/craftsman_list.html', {'craftsmen': craftsmen})

# ユーザー一覧機能
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile

def user_list_view(request):
    query = request.GET.get('q', '').strip()  # 名前検索
    role_filter = request.GET.get('role', '').strip()  # 役割絞り込み

    users_by_role = {}
    for role_value, role_label in Profile.ROLE_CHOICES:
        qs = Profile.objects.filter(role=role_value)
        # GETで指定されている役割だけに絞る
        if role_filter and role_filter != role_value:
            continue
        if query:
            qs = qs.filter(name__icontains=query)
        users_by_role[role_label] = qs

    return render(request, 'accounts/user_list.html', {
        'users_by_role': users_by_role,
        'query': query,
        'role': role_filter,
        'ROLE_CHOICES': Profile.ROLE_CHOICES
    })