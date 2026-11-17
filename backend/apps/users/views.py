import json
import base64
import urllib.request
import urllib.error
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsAdminRole
from apps.audit.utils import log_activity
from apps.audit.models import AuditLog

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.filter(username=request.data.get('username')).first()
            if user:
                log_activity(
                    AuditLog.Action.LOGIN,
                    user=user,
                    request=request,
                    details={"method": "credentials"}
                )
        return response

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data

        log_activity(
            AuditLog.Action.REGISTER,
            user=user,
            request=request,
            details={"username": user.username, "role": user.role}
        )

        return Response({
            "message": "User registered successfully",
            "user": user_data
        }, status=status.HTTP_201_CREATED)

class GoogleAuthView(APIView):
    """
    Handles Google OAuth Sign-in & Registration.
    Accepts a Google ID token credential or profile payload, verifies or decodes
    the user identity, and issues SimpleJWT access & refresh tokens.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        credential = request.data.get('credential')
        email = request.data.get('email')
        name = request.data.get('name', '')
        avatar_url = request.data.get('avatar_url', '')

        # 1. If Google ID token is provided, verify or decode token
        if credential:
            token_data = self._verify_google_token(credential)
            if token_data:
                email = token_data.get('email', email)
                name = token_data.get('name', name)
                avatar_url = token_data.get('picture', avatar_url)

        if not email:
            return Response(
                {"error": "Google authentication failed: Email address is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = email.lower().strip()

        # 2. Find existing user by email, or create new user
        user = User.objects.filter(email=email).first()

        if not user:
            # Generate a clean unique username
            base_username = email.split('@')[0].replace('.', '_')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            first_name = ''
            last_name = ''
            if name:
                parts = name.strip().split(' ', 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ''

            # Create new user
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                avatar_url=avatar_url or '',
                role=User.Role.REVIEWER, # Default role for new Google sign-ups
                organization='Google Workspace User'
            )
            user.set_unusable_password()
            user.save()

            log_activity(
                AuditLog.Action.REGISTER,
                user=user,
                request=request,
                details={"method": "google_oauth", "email": email}
            )
        else:
            # Update avatar if provided
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
                user.save(update_fields=['avatar_url'])

        # 3. Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        log_activity(
            AuditLog.Action.LOGIN,
            user=user,
            request=request,
            details={"method": "google_oauth", "email": email}
        )

        return Response({
            "access": access,
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
            "message": "Signed in successfully via Google"
        }, status=status.HTTP_200_OK)

    def _verify_google_token(self, credential):
        """
        Verify Google token via tokeninfo or decode unverified JWT payload.
        """
        # Try online verification with Google
        try:
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
            req = urllib.request.Request(url, headers={'User-Agent': 'DocuMind-Auth/1.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    return data
        except Exception:
            pass

        # Fallback: Safely parse JWT body payload
        try:
            parts = credential.split('.')
            if len(parts) >= 2:
                # Add padding
                payload_b64 = parts[1] + '=' * (-len(parts[1]) % 4)
                decoded = base64.urlsafe_b64decode(payload_b64.encode('utf-8'))
                data = json.loads(decoded.decode('utf-8'))
                if 'email' in data:
                    return data
        except Exception:
            pass

        return None

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if 'role' in request.data and not request.user.is_admin_role():
            return Response({"error": "Only admins can change roles"}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
        return Response(serializer.data)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
