from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()  # .envからAPIキーを読み込む

#OpenAIクライアントを作成
#iniadのOpenAIサーバーに接続する設定
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.openai.iniad.org/api/v1"
)

#トップページ用のビュー
def index(request):
    return render(request, 'aidea/index.html')  # 工芸品選択ページ

#デザインページ用のビュー
def design(request):
    item_name = request.GET.get('item','')
    return render(request, 'aidea/design.html', {'item_name':item_name})  # デザイン対話ページ

#AI生成用のビュー
#CSRFトークンチェックを無効にして、フロントからPOSTを送れるようにする
@csrf_exempt
def generate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        messages = data.get('messages', [])

        #ここでAIに送っている
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        #フロントJSにデータを返す
        return JsonResponse({"text": response.choices[0].message.content})
    return JsonResponse({"error": "POSTのみ対応"}, status=400)
