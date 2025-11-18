from django.urls import reverse_lazy
from django.views import generic
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product

# 商品一覧
class ProductListView(generic.ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

# 商品詳細
class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'

# 商品作成
class ProductCreateView(LoginRequiredMixin, generic.edit.CreateView):
    model = Product
    fields = ['name', 'description', 'price', 'image', 'category']
    template_name = 'product/product_form.html'
    success_url = reverse_lazy('product:product_list')

    def form_valid(self, form):
        form.instance.craftsman = self.request.user
        return super(ProductCreateView, self).form_valid(form)

# 商品更新
class ProductUpdateView(LoginRequiredMixin, generic.edit.UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'image', 'category']
    template_name = 'product/product_form.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.craftsman != self.request.user:
            raise PermissionDenied('You do not have permission to edit.')
        return super(ProductUpdateView, self).dispatch(request, *args, **kwargs)

# 商品削除
class ProductDeleteView(LoginRequiredMixin, generic.edit.DeleteView):
    model = Product
    template_name = 'product/product_delete.html'
    success_url = reverse_lazy('product:product_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.craftsman != self.request.user:
            raise PermissionDenied('You do not have permission to delete.')
        return super(ProductDeleteView, self).dispatch(request, *args, **kwargs)
