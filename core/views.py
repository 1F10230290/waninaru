from django.shortcuts import render

# Create your views here.

#トップページのビュー関数
def index(request):  #request：Chromeなどのウェブブラウザからサーバーに「ぺージください」とリクエストする
    return render(request, 'core/index.html')  #テンプレート(request)やデータからページ(html)を作って返す