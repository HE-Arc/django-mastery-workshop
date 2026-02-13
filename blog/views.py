
# Create your views here.
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Post
from .serializers import (
    PostSerializer,
    RegisterSerializer,
    LoginSerializer,
    AuthResponseSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    MessageResponseSerializer,
    PasswordResetRequestDebugResponseSerializer,
)

User = get_user_model()


class PostViewSet(ModelViewSet):
    """A viewset for viewing and editing post instances."""
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post = serializer.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "blog_feed",
            {
                "type": "blog_event",
                "data": {
                    "event": "post_created",
                    "id": post.id,
                    "title": post.title,
                    "status": post.status,
                },
            },
        )

    def perform_destroy(self, instance):
        post_id = instance.id
        title = instance.title
        status_value = instance.status
        instance.delete()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "blog_feed",
            {
                "type": "blog_event",
                "data": {
                    "event": "post_deleted",
                    "id": post_id,
                    "title": title,
                    "status": status_value,
                },
            },
        )


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
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Auth"],
    summary="Request password reset",
    description=(
        "Generates a password reset token flow. "
        "Response is generic to avoid leaking account existence."
    ),
    auth=[],
    request=PasswordResetRequestSerializer,
    responses={
        200: PasswordResetRequestDebugResponseSerializer,
    },
)
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


@extend_schema(
    tags=["Auth"],
    summary="Confirm password reset",
    description="Resets the password using uid/token and a new password.",
    auth=[],
    request=PasswordResetConfirmSerializer,
    responses={
        200: MessageResponseSerializer,
        400: OpenApiResponse(description="Invalid token, uid or password payload"),
    },
)
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
            return Response(
                {"detail": "Invalid reset link payload."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, data["token"]):
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(data["new_password"])
        user.save(update_fields=["password"])
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )
