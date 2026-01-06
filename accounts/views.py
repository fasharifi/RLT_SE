from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile


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
        })



