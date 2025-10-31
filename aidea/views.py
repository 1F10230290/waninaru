from django.shortcuts import render, redirect
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
from .models import DesignIdea

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
            "content": f"""
        あなたは{item_name}の専門家であり、素材・技法・意匠に詳しいプロのデザイナーアシスタントです。
        ユーザーが新しい{item_name}のデザインを考え、最終的にスケッチを描けるように、対話を通じてサポートするのがあなたの役割です。

        # 基本原則
        - ユーザーの発想を豊かに広げるため、専門的かつ想像を広げる助言をしてください。
        - ユーザーのアイデアや発言を絶対に否定・制止しないでください。（例：「それは難しい」ではなく「面白いですね。それなら…」と提案する）
        - 表現は短く、詩的すぎず、温かみのある語り口を維持してください。

        # 対話の進め方（最重要）
        - ユーザーから質問や発言を受けたら、必ず「次の一歩の発想を促す質問」または「次のアクションを導く言葉」で回答を締めくくってください。
        - （例：「どんな場面で使いたいですか？」「どんな気持ちを込めたいですか？」「どんなモチーフを思い浮かべますか？」「どちらの雰囲気が好きですか？」）

        # 具体的なサポート技術
        1.  **抽象的なイメージの具体化:**
            ユーザーが「決まっていない」「イメージしにくい」と発言したら、具体的な選択肢や例を3つほど提示してください。（例：使う場面、モチーフの方向性、色のイメージなど）

        2.  **初心者への配慮:**
            ユーザーが「描いたことがない」「初心者だ」と不安を示したら、「大丈夫です」と安心させ、ハードルを下げる提案をしてください。（例：「まずは言葉で描いてみましょう」「簡単な線や配置を考えるだけで十分です」「画像検索で好きなものを選んでみましょう」）

        3.  **専門知識の提供:**
            アイデアが固まってきたら、{item_name}の専門知識（塗りの種類、蒔絵、沈金、吉祥文様、色の象徴など）を使い、デザインをより格調高く、または個性的・現代的にする提案をしてください。
            """
        }

        total_messages = len(messages)

        messages_to_send = []

        if total_messages > 2:
            messages_to_send.extend(messages_to_send[:2])
        else:
            messages_to_send.extend(messages)

        if total_messages >12:
            messages_to_send.extend(messages[-10:])
        elif total_messages > 2:
            messages_to_send.extend(messages[2:])

        #会話の履歴を先頭にプロンプトを挿入する
        messages_with_system_prompt = [system_prompt] + messages_to_send

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


#デザインページ用のビュー
def design(request):
    item_name = request.GET.get('item', '')  # '輪島塗のお椀' など
    
    tips = []  # 注意点リスト初期化
    
    if '輪島塗' in item_name:
        tips = [
            "下地に「地の粉（珪藻土）」を用いるため、やや厚みと重みがあり、立体的な彫りや沈金（金粉彫刻）を活かすデザインが映える。",
            "多層塗りによる深い艶が特徴なので、色数を抑えて漆の光沢や質感を主役にするデザインが◎",
            "表面が硬く丈夫な反面、細かい模様を掘り込みすぎると割れやすいので、過度な細密彫刻は避ける。"
        ]
    elif '会津塗' in item_name:
        tips = [
            "銀粉や色漆などを重ねて描く蒔絵や研ぎ出しが得意なので、絵柄や模様を活かしたデザインが向く。",
            "軽量で、フォルムの繊細さを生かせるため、線の細い模様やグラデーション表現がおすすめ。",
            "加飾面が比較的薄い塗り層なので、厚い盛り上げや重ね塗りのデザインは避けると良い。"
        ]
    elif '有田焼' in item_name:
        tips = [
            "白磁の透明感が魅力なので、**余白を活かしたデザイン（白を見せる構成）**が美しく映える。",
            "細い線や繊細な構図が得意なため、精密な文様や整った幾何学柄が向く。",
            "釉薬の下で発色する呉須（青）の線描が特徴なので、重ね塗りや厚い絵付けは避けると品のある仕上がりになる。"
        ]
    elif '九谷焼' in item_name:
        tips = [
            "厚めの色絵が特徴で、赤・黄・緑・紫・紺青などの鮮やかな配色を大胆に使える。",
            "絵の具に厚みがあるため、立体感のある構図や重ね塗りのグラデーション表現が効果的。",
            "柄を全面に敷き詰めると重く見えることがあるので、中央にモチーフを置いて余白でバランスを取ると上品に仕上がる。"
        ]
    else:
        tips = ["工芸品の特性を活かしたデザインを心がけましょう。"]

    # POSTリクエスト時はアイデア投稿を処理
    if request.method == "POST":
        image = request.FILES.get('image')
        description = request.POST.get('description', '')
        if image and description:
            DesignIdea.objects.create(image=image, description=description)
            return redirect(request.path + f'?item={item_name}')  # 投稿後にリロードしてGETに戻す

    # 投稿済みアイデアも取得して表示可能にする
    ideas = DesignIdea.objects.all().order_by('-created_at')

    context = {
        'item_name': item_name,
        'tips': tips,
        'ideas': ideas  # 投稿一覧をテンプレートで表示可能
    }
    return render(request, 'aidea/design.html', context)

def idea_list(request):
    ideas = DesignIdea.objects.all().order_by('-created_at')
    return render(request, 'aidea/list.html', {'ideas': ideas})