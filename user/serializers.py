from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = { 'password': { 'write_only': True }}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# class LoginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username','password')
    
#     def validate(self, data):
#         user = authenticate(**data)
#         if user and user.is_active:
#             return user
#         raise serializers.ValidationError("Incorrect Credentials")
    
class AuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username")
    password = serializers.CharField(label="Password",style={"input_type":"password"}, trim_whitespace=False)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(request=self.context.get('request'),username=username, password=password)
            if not user:
                msg = 'Unable to login with protected credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password". '
            raise serializers.ValidationError(msg, code='authorization')
        data['user'] = user
        return data