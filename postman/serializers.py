from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['pk', 'sender', 'receiver', 'message', 'subject', 'creation_date', 'read']
    pk = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        required=False,
        )

    sender = serializers.CharField(
        label="Sender",
        required=False,
    )
    receiver = serializers.CharField(
        label="Receiver",
        required=True,
    )

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )

    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username = username, password = password)

            if not user:
                msg = 'Access denied: wrong username and password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name']
    
    username = serializers.CharField(
        label="Username",
        write_only=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    password2 = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    first_name = serializers.CharField(
        label="FirstName",
        required=True
    )

    last_name = serializers.CharField(
        label="LastName",
        required=True
    )

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs['password2']
        username = attrs['username']
        if username and password and password2:
            if password == password2:
                return attrs
            msg = 'Registration denied: passwords do not match.'
            raise serializers.ValidationError(msg, code='authorization')
        msg = 'Registration denied: Must send username, password, email, first name and last name.'
        raise serializers.ValidationError(msg, code='authorization')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user