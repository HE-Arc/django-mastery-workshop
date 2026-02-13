# Module 3 - Authentification JWT et permissions

## Objectifs

- Comparer les strategies d authentification API
- Implementer JWT (access + refresh)
- Proteger le CRUD avec permissions DRF
- Tester des scenarios reels (public vs protege)
- Ajouter un flux mot de passe oublie (request/confirm)

## Prerequis

- Module securite termine
- API CRUD fonctionnelle

## Step by Step

### Step 0 - Activer l environnement virtuel

Windows (PowerShell):

```powershell
env\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source env/bin/activate
```

Installer les dependances:

```bash
pip install -r requirements.txt
```

### Step 1 - Installer JWT

```bash
pip install djangorestframework-simplejwt
```

Creer un utilisateur de test (si besoin):

```bash
python manage.py createsuperuser
```

### Step 2 - Configurer DRF + JWT

Fichier: `newspaper/settings.py`

```python
from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
}
```

### Step 3 - Ajouter les routes token (globales)

Fichier: `newspaper/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("blog.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
```

### Step 4 - Ajouter register / login (metier)

Fichier: `blog/serializers.py` (ajouter)

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
```

Fichier: `blog/views.py` (ajouter)

```python
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import RegisterSerializer, LoginSerializer, AuthResponseSerializer


@extend_schema(
    tags=["Auth"],
    summary="Register a new user",
    description="Creates a user account and returns JWT access/refresh tokens.",
    auth=[],
    request=RegisterSerializer,
    responses={
        201: AuthResponseSerializer,
        400: OpenApiResponse(description="Validation error"),
    },
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Auth"],
    summary="Login with email/password",
    description="Returns JWT access/refresh tokens for an existing user.",
    auth=[],
    request=LoginSerializer,
    responses={
        200: AuthResponseSerializer,
        401: OpenApiResponse(description="Invalid credentials"),
    },
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = User.objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password) or not user.is_active:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": {"id": user.id, "username": user.username, "email": user.email},
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )
```

Fichier: `blog/urls.py` (ajouter)

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    PostViewSet,
    RegisterView,
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/password-reset/request/", PasswordResetRequestView.as_view(), name="auth-password-reset-request"),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
    path("", include(router.urls)),
]
```

### Step 5 - Ajouter mot de passe oublie (request/confirm)

Fichier: `blog/serializers.py` (ajouter)

```python
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        validate_password(attrs["new_password"])
        return attrs
```

Fichier: `blog/views.py` (ajouter)

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

User = get_user_model()


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        response_data = {
            "detail": (
                "If an account exists for this email, "
                "a password reset procedure has been generated."
            )
        }
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            if settings.DEBUG:
                response_data["reset_uid"] = uid
                response_data["reset_token"] = token
        return Response(response_data, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user_id = force_str(urlsafe_base64_decode(data["uid"]))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid reset link payload."}, status=400)

        if not default_token_generator.check_token(user, data["token"]):
            return Response({"detail": "Invalid or expired reset token."}, status=400)

        user.set_password(data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Password has been reset successfully."}, status=200)
```

Note:

- En mode `DEBUG=True`, l endpoint `request` retourne `reset_uid` et `reset_token` pour faciliter les tests en cours.
- En production, envoi via email recommande et reponse toujours generique.

### Step 6 - Proteger le CRUD

Fichier: `blog/views.py`

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from .models import Post
from .serializers import PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
```

Resultat attendu:

- lecture publique (`GET`) autorisee
- ecriture (`POST`, `PUT`, `PATCH`, `DELETE`) reservee aux utilisateurs authentifies

### Step 7 - Permission custom (option)

Fichier a creer: `blog/permissions.py`

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "author_id", None) == getattr(request.user, "id", None)
```

Fichier: `blog/views.py` (si modele avec `author`)

```python
from .permissions import IsAuthorOrReadOnly


class PostViewSet(ModelViewSet):
    # ...
    permission_classes = [IsAuthorOrReadOnly]
```

## Tests de validation

### 1 - Register (creer un compte)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"etudiant1\",\"email\":\"etudiant1@example.com\",\"password\":\"Password123!\",\"password_confirm\":\"Password123!\"}"
```

### 2 - Login (obtenir access + refresh)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"etudiant1@example.com\",\"password\":\"Password123!\"}"
```

### 3 - Password reset request

```bash
curl -X POST http://127.0.0.1:8000/api/auth/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"etudiant1@example.com\"}"
```

### 4 - Password reset confirm (avec uid/token du step 3 en DEBUG)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d "{\"uid\":\"<UID>\",\"token\":\"<TOKEN>\",\"new_password\":\"Password456!\",\"new_password_confirm\":\"Password456!\"}"
```

### 5 - Verification Swagger (important)

1. Ouvrir `http://127.0.0.1:8000/api/docs/`
2. Verifier la presence du tag `Auth`
3. Tester `POST /api/auth/register/`
4. Tester `POST /api/auth/login/`

### 6 - Obtenir un token (endpoint global optionnel)

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin\"}"
```

### 7 - Appel protege sans token

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"JWT test\",\"content\":\"Contenu long ...\",\"status\":\"draft\"}"
```

### 8 - Appel protege avec token

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"JWT OK\",\"content\":\"Contenu long pour valider la creation.\",\"status\":\"draft\"}"
```

### 9 - Refresh token

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"<REFRESH_TOKEN>\"}"
```

## Erreurs frequentes

- Oublier le prefix `Bearer <token>`
- Mettre JWT sans permissions
- Confondre authentification (qui je suis) et autorisation (ce que je peux faire)

## Exercice de fin

1. Activer JWT
2. Proteger create/update/delete
3. Laisser read public
4. Demonstration complete via Swagger ou Postman

## Checklist fin de module

- JWT operationnel
- Routes token operationnelles
- Permissions appliquees
- Scenarios de test passes
