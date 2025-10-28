from django.db import models
from django.conf import settings
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage

s3_storage = S3Boto3Storage()

# タグモデル（伝統工芸カテゴリ用）
class CraftTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# プロジェクトモデル
class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    goal_amount = models.PositiveIntegerField(default=0)
    current_amount = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    supporter_count = models.PositiveIntegerField(default=0)  # 現在の支援者数
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()  # プロジェクト終了日時
    image = models.ImageField(upload_to='project_images/', storage=s3_storage, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # CustomUserに対応
        on_delete=models.CASCADE,
        related_name='projects'
    )
    tags = models.ManyToManyField(CraftTag, blank=True)  # 伝統工芸タグ

    def __str__(self):
        return self.title

    # 残り日数を計算するプロパティ
    @property
    def days_left(self):
        delta = self.end_date - timezone.now()
        return max(delta.days, 0)

    # 作成者名（Profile.name）を返すプロパティ
    @property
    def creator_name(self):
        try:
            return self.created_by.profile.name
        except Exception:
            return self.created_by.email  # Profile がない場合は email を返す

# 支援（リターン）モデル
class Reward(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='rewards')
    title = models.CharField(max_length=100)  # リターン名
    description = models.TextField(blank=True)
    amount = models.PositiveIntegerField()  # 支援金額
    limit = models.PositiveIntegerField(null=True, blank=True)  # 限定数（任意）

    def __str__(self):
        return f"{self.title} ({self.amount}円)"

# いいねモデル
class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # CustomUserに対応
        on_delete=models.CASCADE
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')  # ユーザーは1プロジェクト1回のみ

    def __str__(self):
        return f"{self.user.email} → {self.project.title}"
