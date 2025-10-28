from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Project, Like, Reward
from .forms import ProjectForm, RewardFormSet
import stripe

# Stripeの初期化
stripe.api_key = settings.STRIPE_SECRET_KEY

# -----------------------------
# プロジェクト一覧ページ
# -----------------------------
def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'funding/project_list.html', {'projects': projects})

# -----------------------------
# プロジェクト詳細ページ
# -----------------------------
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    rewards = project.rewards.all()  # プロジェクトに紐づくリターン一覧

    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, project=project).exists()

    return render(request, 'funding/project_detail.html', {
        'project': project,
        'user_liked': user_liked,
        'rewards': rewards
    })

# -----------------------------
# いいね切り替え
# -----------------------------
@login_required
def toggle_like(request, pk):
    project = get_object_or_404(Project, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, project=project)

    if not created:
        # すでにいいね済み → 解除
        like.delete()
        status = 'unliked'
    else:
        # 新規いいね
        status = 'liked'

    # いいね数をキャッシュ更新
    project.like_count = Like.objects.filter(project=project).count()
    project.save()

    # Ajax対応
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': status, 'like_count': project.like_count})

    return redirect('project_detail', pk=pk)

@login_required
def liked_projects(request):
    # ログインユーザーがいいねしたプロジェクトを取得
    projects = Project.objects.filter(like__user=request.user).distinct()

    return render(request, 'funding/liked_projects.html', {
        'projects': projects
    })

# -----------------------------
# Stripe支払い（リターン対応）
# -----------------------------
@login_required
def create_checkout_session(request, pk):
    project = get_object_or_404(Project, pk=pk)
    amount = int(request.POST.get('amount', 1000))  # デフォルト1000円

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'jpy',
                'product_data': {'name': project.title},
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/funding/{project.pk}/thanks/'),
        cancel_url=request.build_absolute_uri(f'/funding/{project.pk}/'),
    )

    return redirect(session.url)


# プロジェクト作成
@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        formset = RewardFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()

            # リターンの保存
            rewards = formset.save(commit=False)
            for reward in rewards:
                reward.project = project
                reward.save()

            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
        formset = RewardFormSet()

    return render(request, 'funding/project_create.html', {'form': form, 'formset': formset})

# 支払い完了
@login_required
def thanks(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'funding/thanks.html', {'project': project})