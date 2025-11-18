from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)

app_name = 'product'

urlpatterns = [
    # 商品一覧
    path('', ProductListView.as_view(), name='product_list'),

    # 商品詳細
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # 商品作成
    path('create/', ProductCreateView.as_view(), name='product_form'),

    # 商品更新
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),

    # 商品削除
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
]
