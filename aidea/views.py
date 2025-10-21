from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
import base64
from django.conf import settings
from PIL import Image
import io

load_dotenv()  # .envからAPIキーを読み込む

#OpenAIクライアントを作成
#iniadのOpenAIサーバーに接続する設定
chat_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://api.openai.iniad.org/api/v1"
)

official_openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY_Teacher")
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
        #フロントエンドから現在の会話履歴を受け取る
        messages = data.get('messages', [])

        #工芸品名を受け取る
        item_name = data.get('get_name', '日本の伝統工芸品')

        #AIの基本設定となるシステムプロンプトを作成する
        system_prompt={
            "role": "system",
            "content": """
            あなたは、「{item_name}」専門の工芸士であり、その魅力を若いクリエイターに伝えるAIデザインパートナーです。

            # あなたの役割
            - 対話相手は、イラストレーターやクリエイターです。
            - あなたは、クリエイターが伝統工芸品のデザインを考案する初期段階の、アイデアの壁打ち相手です。新しい発想を促したりします。
            - ユーザーは工芸品のデザインを描くのであり、工芸品そのものを制作するわけではない点に注意してください。
            - 描くのは単なるアイデアでなく、実際に製品化する可能性があることを念頭において、常にリアルな視点を持って考えてください。

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
        response = chat_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_with_system_prompt,
            max_tokens=500
        )
        
        #フロントJSにデータを返す
        return JsonResponse({"text": response.choices[0].message.content})
    return JsonResponse({"error": "POSTのみ対応"}, status=400)

# aidea/views.py

# ... (既存のimportやクライアント定義、他のビューはそのまま) ...


# ▼▼▼ 新しいフィードバック用のビューを追加 ▼▼▼
@csrf_exempt
def get_feedback(request):
    if request.method == 'POST':
        design_image = request.FILES.get('design_image')
        if not design_image:
            return JsonResponse({"error": "画像ファイルがありません。"}, status=400)
        
        # URLから工芸品名を取得
        # 'item' は design ビューに渡されるクエリパラメータ。
        # 実際にはJSから送るのが確実ですが、ここではセッションやリファラから取得する簡易的な例を示します。
        item_name = request.POST.get('item_name', '日本の伝統工芸品')

        try:
            # 画像をbase64形式のテキストにエンコード
            base64_image = base64.b64encode(design_image.read()).decode('utf-8')

            # GPT-4Vに送るための、フィードバックに特化したプロンプト
            feedback_prompt = f"""
            あなたは、日本の伝統工芸品の魅力を若いクリエイターに伝える、親切なAIデザインパートナーです。
            添付された画像は、「{item_name}」のデザイン案です。
            このデザインについて、以下の構成で具体的なフィードバックをMarkdown形式で返してください。

            ### 1. 素晴らしい点
            まず、このデザインの最も優れている点、魅力的な点を褒めてください。クリエイターの意欲を高めることが重要です。

            ### 2. さらに良くするための提案
            次に、このデザインを製品化する上での**技術的な実現可能性**を厳しく評価してください。特に、**複雑な凹凸表現、細かい線、色のグラデーション**などが、この「{item_name}」の製法で本当に実現可能か、あなたの専門知識を基に入念にチェックしてください。
            - **もし課題がある場合**: 「【製造上の課題】」という見出しで、実現が難しい部分とその技術的な理由を明確に指摘し、デザインの意図を尊重した代替案を提案してください。
            - **もし課題がない場合**: 「【技術的な懸念なし】」という見出しで、「このデザインは{item_name}の特性をよく理解しており、技術的な問題点はありません」と述べ、その上でデザインをさらに引き立てるためのプロ向けの豆知識を共有してください。
            
            ### 3. 総評
            最後に、全体をポジティブにまとめる一言をお願いします。
            """

            # GPT-4 (gpt-4-turbo) APIを呼び出す
            vision_response = official_openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": feedback_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800
            )

            feedback_text = vision_response.choices[0].message.content
            return JsonResponse({"feedback": feedback_text})

        except Exception as e:
            print(f"画像フィードバック処理エラー: {e}")
            return JsonResponse({"error": f"AIとの通信中にエラーが発生しました: {e}"}, status=500)

    return JsonResponse({"error": "POSTリクエストのみ対応"}, status=400)