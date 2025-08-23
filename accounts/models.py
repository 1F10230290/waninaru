from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = None  # usernameは使わずemailをIDに
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # 必須項目からusernameを外す

    # groups と user_permissions の関連名を変えて衝突を回避
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # ここを変更
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',  # ここを変更
        blank=True
    )

class Profile(models.Model):
    ROLE_CHOICES = [
        ('supporter', 'サポーター'),
        ('creator', 'クリエイター'),
        ('craftsman', '工芸士'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='icons/', blank=True, null=True)
    bio = models.TextField(max_length=200, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

