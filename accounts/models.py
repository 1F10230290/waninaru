from django.db import models
from django.contrib.auth.models import AbstractUser
from storages.backends.s3boto3 import S3Boto3Storage
from .managers import CustomUserManager

s3_storage = S3Boto3Storage()

# カスタムユーザーモデル
class CustomUser(AbstractUser):
    # メールアドレスを一意のIDとして使用
    email = models.EmailField(unique=True)

    # username フィールドは使用しない
    username = None  # usernameは使わずemailをIDに

    # 認証用フィールドを email に設定
    USERNAME_FIELD = 'email'

    # 新規作成時に必須項目から username を外す
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    # groups と user_permissions の関連名を変更して衝突回避
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank=True
    )

# ユーザープロフィールモデル
class Profile(models.Model):
    # ユーザーの役割の選択肢
    ROLE_CHOICES = [
        ('supporter', 'サポーター'),
        ('creator', 'クリエイター'),
        ('craftsman', '工芸士'),
    ]

    # CustomUser と 1対1のリレーション
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # プロフィール名
    name = models.CharField(max_length=50)

    # ユーザーアイコン画像
    icon = models.ImageField(upload_to='icons/', storage=s3_storage, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # 自己紹介文
    bio = models.TextField(max_length=200, blank=True)

    # ユーザーの役割
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

# 工芸士情報
class CraftsmanProfile(models.Model):
    profile = models.OneToOneField(
        'Profile', on_delete=models.CASCADE, related_name='craftsman_info'
    )
    specialty = models.CharField("専門分野", max_length=100, blank=True)
    experience_years = models.PositiveIntegerField("経験年数", blank=True, null=True)
    workshop_location = models.CharField("工房の所在地", max_length=200, blank=True)
    bio = models.TextField("自己紹介", max_length=500, blank=True)
    registered = models.BooleanField(default=False)  # 本登録フラグ

    def __str__(self):
        return f"{self.profile.name}の工芸士情報"