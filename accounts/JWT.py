from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Profile, SMSVerification


class PhoneTokenSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField()

    def validate(self, attrs):
        phone = attrs.get("phone_number")
        password = attrs.get("password")

        try:
            profile = Profile.objects.get(phone_number=phone)
            user = profile.user
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Invalid phone number or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid phone number or password")

        if not user.is_active:
            raise serializers.ValidationError("Phone number not verified")

        if not SMSVerification.objects.filter(
            user=user, is_verified=True
        ).exists():
            raise serializers.ValidationError("Phone number not verified")

        token = self.get_token(user)
        return {
            "refresh": str(token),
            "access": str(token.access_token)
        }