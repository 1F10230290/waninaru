from django.urls import path
from . import views

urlpatterns = [
    path('room/<str:room_name>/', views.chat_room_view, name='chat_room'),
    path('start/<int:craftsman_id>/', views.start_chat_view, name='start_chat'),
    path('start_by_craftsman/<int:creator_id>/', views.start_chat_by_craftsman_view, name='start_chat_by_craftsman'),
    path('room/<str:room_name>/send/', views.send_message, name='send_message'),
    path('room/<str:room_name>/get/', views.get_messages, name='get_messages'),
    path("room/<str:room_name>/delete/", views.delete_chat_room, name="delete_chat_room"),
    path("", views.active_chat_rooms, name="active_chat_rooms"),
]
