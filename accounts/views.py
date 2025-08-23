from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignUpForm, ProfileForm
from .models import Profile

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ログインさせる
            return redirect('profile_setup')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def profile_setup_view(request):
    # 既存のProfileを取得、なければ新規作成
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('mypage')  # 保存後マイページへ
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_setup.html', {'form': form})

def login_view(request):
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='accounts/login.html')(request)

def mypage_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/mypage.html', {'profile': profile})
