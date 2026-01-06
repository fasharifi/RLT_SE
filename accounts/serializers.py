from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Role, Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions']


class ProfileSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'birthdate', 'phone_number', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('phone_number', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        phone_number = validated_data['phone_number']

        # Check if a user already exists with this phone number
        if User.objects.filter(username=phone_number).exists():
            raise serializers.ValidationError("User with this phone number already exists.")



        user = User.objects.create_user(
            username=phone_number,   # use phone_number as username
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),

        )

        Profile.objects.create(
            user=user ,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            birthdate=validated_data.get('birthdate', ''),
            phone_number=validated_data.get('phone_number', ''),
        )

        return user



class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)