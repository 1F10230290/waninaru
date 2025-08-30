from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, ProfileForm
from .models import Profile

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

# プロフィール設定用ビュー
def profile_setup_view(request):
    # 既存のProfileを取得、なければ新規作成
    profile, created = Profile.objects.get_or_create(user=request.user)  # get_or_create で1回で済ませる

    if request.method == 'POST':
        # request.FILES を渡すことでアップロード画像も保存可能
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():  # バリデーションチェック
            form.save()  # プロフィールを保存（画像は MEDIA_ROOT に保存され、同期フォルダにも反映）
            return redirect('mypage')  # 保存後にマイページへリダイレクト
    else:
        form = ProfileForm(instance=profile)  # GET の場合は既存情報でフォームを作成

    # テンプレートにフォームを渡す
    return render(request, 'accounts/profile_setup.html', {'form': form})

# ログイン用ビュー
def login_view(request):
    from django.contrib.auth.views import LoginView  # Django 標準の LoginView を使用
    # template_name を指定して呼び出す
    return LoginView.as_view(template_name='accounts/login.html')(request)

# マイページ用ビュー
def mypage_view(request):
    # ユーザーに紐づく Profile を取得
    profile = Profile.objects.get(user=request.user)
    # テンプレートに profile を渡す
    return render(request, 'accounts/mypage.html', {'profile': profile})
