from django.urls import path

from . import views

app_name = 'postman'
urlpatterns = [
    path('', views.index, name='index'),
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('messages/<int:pk>', views.SingleMessageView.as_view(), name='single_message'),
    path('messages/unread/', views.UnreadMessagesView.as_view() ,name = 'unread_messages'),
    path('messages/user/<int:user_key>', views.UserMessagesView.as_view(), name='user_messages'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register')
]