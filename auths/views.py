# This allows public access (no authentication)

from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.pagination import PageNumberPagination
import random
from django.utils import timezone
import string
from django.contrib.auth import login, get_user_model, update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import  get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserProfile
from rest_framework import viewsets, permissions
from .serializers import (
    UserRegisterSerializer, LoginSerializer, UserSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, PasswordChangeSerializer, CustomUserAllSerializer
)
from rest_framework.authentication import TokenAuthentication



User = get_user_model()


def success_response(message, data, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "statusCode": status_code,
        "message": message,
        "data": data
    }, status=status_code)


def failure_response(message, error, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "statusCode": status_code,
        "message": message,
        "error": error
    }, status=status_code)

# Postal Code Validator


def is_valid_postal_code(postal_code):
    return postal_code.startswith('9')

class PostalCodeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        postal_code = request.data.get("postal_code")
        if is_valid_postal_code(postal_code):
            email = request.data.get("email")  
            user = get_user_model().objects.filter(email=email).first()
            
            if user:
                return Response({"message": "User already registered, redirecting to login."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User is new, redirecting to registration."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Postal code is not valid. It should start with '9'."}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        # Proceed with the regular update logic
        serializer = self.get_serializer(
            instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return success_response("Profile updated successfully", serializer.data)


class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(self, user):
        refresh_token = super().for_user(user)

        # Add custom claims
        refresh_token.payload['username'] = user.username
        refresh_token.payload['email'] = user.email
        refresh_token.payload['role'] = user.role

        return refresh_token

from django.contrib.auth.backends import ModelBackend
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            if not user.is_active:
                user.is_active = True
                user.save()
            # user = serializer.validated_data['user']

            refresh = CustomRefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = success_response(
                'Register Successful.',
                {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            )

            response.set_cookie('refresh_token', refresh_token,
                                httponly=True, secure=True)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return response

        return failure_response('Something went wrong.', serializer.errors)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = CustomRefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = Response({
                'success': True,
                'statusCode': status.HTTP_200_OK,
                'message': 'Login successful',
                'data': {
                    'access': access_token,
                    'refresh': refresh_token,
                }
            })

            response.set_cookie('refresh_token', refresh_token,
                                httponly=True, secure=True)
            login(request, user)
            return response

        # Directly return a Response instead of using failure_response
        return Response({
            'success': False,
            'statusCode': status.HTTP_400_BAD_REQUEST,
            'message': 'Invalid credentials',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

                response = success_response("Logout successful")
                # Delete the refresh token cookie
                response.delete_cookie('refresh_token')
                return response
            return failure_response("Refresh token not provided")
        except Exception as e:
            return failure_response("Logout failed", str(e), status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    """API endpoint for retrieving the latest About Us section."""
    permission_classes = [AllowAny]
    # Allows token authentication, even expired tokens
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate and create a new access token
            new_access = RefreshToken(refresh_token).access_token
            return Response(
                {"access": str(new_access)},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # Check if the old password is correct
        if not user.check_password(old_password):
            return failure_response("Incorrect old password", {"detail": "Incorrect old password"}, status.HTTP_400_BAD_REQUEST)

        # Update password
        user.set_password(new_password)
        user.save()

        # Update session to prevent logout after password change
        update_session_auth_hash(request, user)

        return success_response({"message": "Password changed successfully"}, status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    """Send OTP to user's email for password reset"""
    permission_classes= [AllowAny]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return failure_response({"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate a random OTP of 6 characters, consisting of numbers and letters
        otp = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6))

        # Save OTP in user profile
        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        user_profile.otp = otp
        user_profile.otp_created_at = timezone.now()
        user_profile.save()

        # Send OTP email
        email_subject = "Your OTP for Password Reset"
        email_body = render_to_string(
            'reset_password_email.html', {'otp': otp})
        email = EmailMultiAlternatives(email_subject, '', to=[user.email])
        email.attach_alternative(email_body, "text/html")
        email.send()

        return success_response("Please check your email for OTP.", {user.email}, status.HTTP_200_OK)


class ValidateOTPView(APIView):
    """Validate OTP before allowing password reset"""

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user_profile = UserProfile.objects.get(user__email=email)
        except UserProfile.DoesNotExist:
            return failure_response({"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if OTP matches and is not expired
        if user_profile.otp == otp:
            if user_profile.is_otp_expired():
                return failure_response({"message": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            return success_response("Successfully OTP Verified. Proceed with password reset.", {}, status.HTTP_200_OK)

        return failure_response({"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """Reset password using OTP"""

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        serializer = ResetPasswordSerializer(data=request.data)

        if not email or not otp:
            return failure_response({"message": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']

        try:
            user_profile = UserProfile.objects.get(user__email=email)
        except UserProfile.DoesNotExist:

            return failure_response({"message": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if user_profile.otp == otp and not user_profile.is_otp_expired():
            user = user_profile.user
            user.password = make_password(new_password)  # Hash new password
            user.save()

            # Clear OTP after reset
            user_profile.otp = None
            user_profile.save()

            return success_response("Password reset successfully.", {}, status.HTTP_200_OK)

        return failure_response({"message": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)





class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Custom View for All Users
class AllUsers(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).order_by('id')
    serializer_class = CustomUserAllSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = CustomPagination

    # GET - Retrieve List of Active Users
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return success_response("User list retrieved successfully", serializer.data)
        except Exception as e:
            return failure_response("Failed to retrieve user list", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST - Create a New User
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response("User created successfully", serializer.data, status.HTTP_201_CREATED)
            return failure_response("User creation failed", serializer.errors)
        except Exception as e:
            return failure_response("An error occurred while creating the user", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    # GET - Retrieve a Single User
    def retrieve(self, request, pk=None):
        try:
            user = get_object_or_404(User, pk=pk, is_active=True)
            serializer = self.get_serializer(user)
            return success_response("User details retrieved successfully", serializer.data)
        except Exception as e:
            return failure_response("Failed to retrieve user details", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    # PUT - Update a User
    def update(self, request, pk=None):
        try:
            user = get_object_or_404(User, pk=pk, is_active=True)
            serializer = self.get_serializer(
                user, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return success_response("User updated successfully", serializer.data)
            return failure_response("User update failed", serializer.errors)
        except Exception as e:
            return failure_response("An error occurred while updating the user", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    # PATCH - Partially Update a User
    def partial_update(self, request, pk=None):
        try:
            user = get_object_or_404(User, pk=pk, is_active=True)
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return success_response("User partially updated successfully", serializer.data)
            return failure_response("User partial update failed", serializer.errors)
        except Exception as e:
            return failure_response("An error occurred while partially updating the user", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    # DELETE - Deactivate a User (Soft Delete)
    def destroy(self, request, pk=None):
        try:
            user = get_object_or_404(User, pk=pk, is_active=True)
            user.is_active = False  # Soft delete instead of hard delete
            user.save()
            return success_response("User deactivated successfully", None, status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return failure_response("Failed to deactivate user", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

