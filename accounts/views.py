from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView

from .JWT import PhoneTokenSerializer
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, SMSVerification
from .utils import send_sms_to_user

"""
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        # Authenticate user via phone_number
        try:
            profile = Profile.objects.get(phone_number=phone_number)
            user = authenticate(request, username=profile.user.username, password=password)
        except Profile.DoesNotExist:
            return Response({"error": "Profile does not exist"}, status=status.HTTP_401_UNAUTHORIZED)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "phone_number": profile.phone_number,
                "role": profile.role.name
            }
        })"""


class LoginViewSets(viewsets.ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)



class UserViewSet(viewsets.ViewSet):

    # 1️⃣ Register
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        profile = Profile.objects.get(user=user)
        #verification = SMSVerification.objects.get(user=user)


        #send_sms_to_user(profile.phone_number, verification.code)

        return Response(
            {"message": "Account created. Verification code sent."},
            status=status.HTTP_201_CREATED
        )

    # 2️⃣ Verify SMS
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_sms(self, request):
        phone = request.data.get("phone_number")
        code = request.data.get("code")

        try:
            profile = Profile.objects.get(phone_number=phone)
            verification = SMSVerification.objects.get(user=profile.user)
        except (Profile.DoesNotExist, SMSVerification.DoesNotExist):
            return Response({"error": "Invalid phone number"}, status=400)

        if verification.code != code:
            return Response({"error": "Invalid verification code"}, status=400)

        verification.is_verified = True
        verification.save()

        user = profile.user
        user.is_active = True
        user.save()

        return Response({"message": "Phone verified successfully"})

    # 3️⃣ Get Profile
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data)

    # 4️⃣ Update Profile
    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        serializer = ProfileSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



