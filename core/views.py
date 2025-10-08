from django.shortcuts import render
import openai
import os

openai.api_key=os.getenv("OPENAI_API_KEY")
# Create your views here.

#トップページのビュー関数
def index(request):  #request：Chromeなどのウェブブラウザからサーバーに「ぺージください」とリクエストする
    return render(request, 'core/index.html')  #テンプレート(request)やデータからページ(html)を作って返す