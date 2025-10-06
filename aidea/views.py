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
        #1 フロントエンドから現在の会話履歴を受け取る
        messages = data.get('messages', [])

        #2 AIの基本設定となるシステムプロンプトを作成する
        system_prompt={
            "role": "system",
            "content": """
        あなたは日本の伝統工芸品のデザインを支援する、親切なAIアシスタントです。

        # あなたの役割
        - ユーザーのデザインアイデアを褒めて、創造性を引き出す手助けをします。
        - 質問には、専門用語を避け、初心者にも分かりやすい言葉で回答します。

        # 制約条件
        - 回答は常に300文字以内の簡潔なものにしてください。
        - ユーザーを決して否定せず、ポジティブな言葉遣いを徹底してください。
        - 箇条書きを使うと分かりやすい場合は、積極的に使用してください。
        - 箇条書きや太字など、Markdown形式を積極的に使用して分かりやすく説明してください。
        - 箇条書きを使う際は、各項目の先頭にハイフン(-)をつけ、必ず改行してください。
        """
        }

        #会話の履歴を先頭にプロンプトを挿入する
        messages_with_system_prompt = [system_prompt] + messages

        #ここでAIに送っている
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_with_system_prompt,
            max_tokens=350
        )
        
        #フロントJSにデータを返す
        return JsonResponse({"text": response.choices[0].message.content})
    return JsonResponse({"error": "POSTのみ対応"}, status=400)
