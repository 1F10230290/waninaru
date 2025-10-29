from django.db import models
from django.conf import settings  
from storages.backends.s3boto3 import S3Boto3Storage

s3_storage = S3Boto3Storage()

class Category(models.Model):                 #伝統工芸品のカテゴリ
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):                  #伝統工芸品の詳細情報
    name = models.CharField("商品名", max_length=255)
    description = models.TextField("説明", blank=True)
    price = models.DecimalField("価格", max_digits=10, decimal_places=2)
    image = models.ImageField("商品画像", upload_to='products/', storage=s3_storage, blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="カテゴリ")
    craftsman = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # accounts.models.CustomUserから
        on_delete=models.CASCADE,
        verbose_name="工芸士",
        related_name='products'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
