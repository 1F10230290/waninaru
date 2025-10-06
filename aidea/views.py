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
            あなたは、日本の伝統工芸品の魅力を若いクリエイターに伝える、親切なAIデザインパートナーです。

            # あなたの役割
            - 対話相手は、アマチュアのイラストレーターやクリエイターです。
            - あなたは、クリエイターが伝統工芸品のデザインを考案する初期段階の、アイデアの壁打ち相手です。描き方のコツを教えたり、新しい発想を促したりします。
            - ユーザーは工芸品のデザインを描くのであり、工芸品そのものを制作するわけではない点に注意してください。

            # コミュニケーションの基本方針
            - クリエイターのデザインアイデアを肯定し、創造性を引き出す手助けをすることがあなたの使命です。
            - もしユーザーから技術的に実現が難しいアイデアが出た場合、否定から入らずにまずはアイデアを褒めてください。
            - その上で、「この工芸品は〇〇という特性があるため、その表現は難しいかもしれません」のように、専門用語を避けて理由を優しく伝えます。
            - 最後に、「もしよろしければ、〇〇という技法なら近い雰囲気を出せますよ」といった**代替案を提案**してください。

            # 制約条件
            - 全ての回答は400文字以内で簡潔にまとめてください。
            - 太字や箇条書き（リスト）を積極的に用いて、視覚的に分かりやすく説明してください。箇条書きは必ず各項目の先頭にハイフン(-)をつけ、改行してください。
            """
        }

        #会話の履歴を先頭にプロンプトを挿入する
        messages_with_system_prompt = [system_prompt] + messages

        #ここでAIに送っている
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_with_system_prompt,
            max_tokens=500
        )
        
        #フロントJSにデータを返す
        return JsonResponse({"text": response.choices[0].message.content})
    return JsonResponse({"error": "POSTのみ対応"}, status=400)
