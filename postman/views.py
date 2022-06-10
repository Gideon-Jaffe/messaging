from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse,JsonResponse
from .models import Message
from rest_framework import views, permissions
from django.contrib.auth import login
from django.contrib.auth.models import User
from . import serializers
# Create your views here.

def index(request):
    return HttpResponse("Hello, world!")

class MessagesView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.MessageSerializer()

    def get(self, request):
        items = Message.objects.filter(receiver=request.user.pk)
        serializer = serializers.MessageSerializer(items, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        serializer = serializers.MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['sender'] = request.user
            rec = User.objects.filter(username=serializer.validated_data['receiver'])
            if rec.__len__() < 1:
                return JsonResponse({'detail': 'No such user'}, status=400)
            serializer.validated_data['receiver'] = rec[0]
            serializer.save()
            return JsonResponse(serializer.data, status=201) #created status
        return JsonResponse(serializer.errors, status=400)

class UnreadMessagesView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.MessageSerializer()

    def get(self, request):
        items = Message.objects.filter(receiver=request.user.pk, read=False)
        serializer = serializers.MessageSerializer(items, many=True)
        return JsonResponse(serializer.data, safe=False)

class UserMessagesView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.MessageSerializer()

    def get(self, request, user_key):
        messages = get_list_or_404(Message, receiver=user_key)
        serializer = serializers.MessageSerializer(messages, many = True)
        return JsonResponse(serializer.data, safe=False)

class SingleMessageView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.MessageSerializer()

    def get(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        if message.sender != request.user and message.receiver != request.user:
            return JsonResponse({'detail': 'Unauthorized'}, status=403)
        message.read = True
        message.save()
        serializer = serializers.MessageSerializer(message)
        return JsonResponse(serializer.data)

    def delete(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        if message.sender != request.user and message.receiver != request.user:
            return JsonResponse({'detail': 'Unauthorized'}, status=403)
        message.delete()
        return JsonResponse({'detail': 'Deleted'}, status = 204)

class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format=None):
        serializer = serializers.LoginSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return HttpResponse(status=202)
        return JsonResponse(serializer.errors, status=400)

class RegisterView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    serializer_class = serializers.RegisterSerializer()

    def post(self, request, formay=None):
        serializer = serializers.RegisterSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return HttpResponse(status=202)
        return JsonResponse(serializer.errors, status=400)



