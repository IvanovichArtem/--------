from rest_framework import serializers
from .models import User, Task
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone', 'role']
        
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            password=make_password(validated_data['password']),
            email=validated_data['email'],
            phone=validated_data['phone'],
            role=validated_data['role']
        )
        user.save()
        return user

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone']
        
        
class TaskSerializer(serializers.ModelSerializer):
    customer = serializers.CharField() 

    class Meta:
        model = Task
        fields = '__all__'