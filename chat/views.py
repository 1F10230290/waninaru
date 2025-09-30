from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Room, Message
from accounts.models import CustomUser
from django.http import JsonResponse
from django.utils import timezone

# チャットルームの作成
@login_required
def chat_room_view(request, room_name):
    room = get_object_or_404(Room, name=room_name)

    # 参加者チェック
    if request.user not in [room.creator, room.craftsman]:
        return render(request, 'chat/not_allowed.html')

    # 相手の名前を計算
    if room.creator == request.user:
        other_name = room.craftsman.profile.name
    else:
        other_name = room.creator.profile.name

    # テンプレートに渡す
    return render(request, 'chat/room.html', {
        'room_name': room.name,
        'other_name': other_name
    })

# クリエイターが工芸士を選んで個別チャットを開始する
@login_required
def start_chat_view(request, craftsman_id):
    creator = request.user
    craftsman = get_object_or_404(CustomUser, id=craftsman_id)

    # Room 名は creator_id と craftsman_id の組み合わせでユニーク
    room_name = f"{creator.id}_{craftsman.id}"

    # Room が存在しなければ作成
    room, created = Room.objects.get_or_create(
        name=room_name,
        defaults={'creator': creator, 'craftsman': craftsman}
    )

    # チャットルームページへリダイレクト
    return redirect('chat_room', room_name=room.name)

#工芸士がクリエイターを選んで個別チャットを開始する
@login_required
def start_chat_by_craftsman_view(request, creator_id):
    craftsman = request.user
    creator = get_object_or_404(CustomUser, id=creator_id)

    # Room 名は creator_id と craftsman_id の組み合わせでユニーク
    room_name = f"{creator.id}_{craftsman.id}"

    # Room が存在しなければ作成
    room, created = Room.objects.get_or_create(
        name=room_name,
        defaults={'creator': creator, 'craftsman': craftsman}
    )

    # チャットルームページへリダイレクト
    return redirect('chat_room', room_name=room.name)

# メッセージ送信
@login_required
def send_message(request, room_name):
    if request.method == "POST":
        room = Room.objects.get(name=room_name)
        content = request.POST.get('message', '').strip()
        if content:
            msg = Message.objects.create(room=room, sender=request.user, content=content)

            # 日本時間に変換
            jp_time = timezone.localtime(msg.timestamp)
            formatted_time = jp_time.strftime("%m/%d %H:%M")  # 月/日 時:分

            return JsonResponse({
                "username": msg.sender.profile.name,
                "message": msg.content,
                "timestamp": formatted_time
            })
    return JsonResponse({"error": "Invalid request"}, status=400)

# メッセージ受信
@login_required
def get_messages(request, room_name):
    room = Room.objects.get(name=room_name)
    messages = room.messages.order_by('timestamp')
    data = [
        {"username": m.sender.profile.name, "message": m.content, "timestamp": m.timestamp.strftime("%H:%M:%S")}
        for m in messages
    ]
    return JsonResponse(data, safe=False)

from django.shortcuts import render

from django.contrib import messages

# チャットルームの削除
@login_required
def delete_chat_room(request, room_name):
    room = get_object_or_404(Room, name=room_name)

    # 削除権限チェック（参加者のみ）
    if request.user not in [room.creator, room.craftsman]:
        return render(request, 'chat/not_allowed.html')

    if request.method == "POST":
        room.delete()
        messages.success(request, "チャットルームを削除しました。")
        return redirect("active_chat_rooms")  # 削除後のリダイレクト先（トップなど）

    return render(request, "chat/confirm_delete.html", {"room": room})

@login_required
def active_chat_rooms(request):
    user = request.user

    # 自分が参加しているルームを取得
    rooms = Room.objects.filter(creator=user) | Room.objects.filter(craftsman=user)

    # 相手の名前を計算してテンプレートに渡す
    room_list = []
    for room in rooms.distinct():
        if room.creator == user:
            other_name = room.craftsman.profile.name
        else:
            other_name = room.creator.profile.name
        room_list.append({
            "name": room.name,
            "other_name": other_name,
        })

    return render(request, "chat/index.html", {"rooms": room_list})