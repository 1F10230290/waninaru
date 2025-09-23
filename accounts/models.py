from django.db import models
from django.contrib.auth.models import AbstractUser


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
    icon = models.ImageField(upload_to='icons/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # 自己紹介文
    bio = models.TextField(max_length=200, blank=True)

    # ユーザーの役割
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

