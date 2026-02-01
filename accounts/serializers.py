from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, Role, Permission, SMSVerification
from .utils import generate_otp


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

    def validate_phone_number(self, value):
        if Profile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value

    def create(self, validated_data):
        phone_number = validated_data['phone_number']

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

        SMSVerification.objects.create(
            user=user,
            code=generate_otp()
        )

        return user



class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data["phone_number"]
        password = data["password"]

        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("User")

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.profile.role.name,
        }