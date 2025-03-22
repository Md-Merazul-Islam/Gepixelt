from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
User = get_user_model()

from utils.upload_utils import upload_file_to_digital_ocean

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # Temporary field for image upload (write-only)
    photo_tmp = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email',  'role', 'address',
                  'phone_number', 'photo', 'photo_tmp')
        read_only_fields = ('id','username', 'email', )

    def create(self, validated_data):
        # Handle image upload if provided
        photo_tmp = validated_data.pop('photo_tmp', None)

        if photo_tmp:
            uploaded_image_url = upload_file_to_digital_ocean(photo_tmp)
            validated_data['photo'] = uploaded_image_url  

        user = User.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        # Handle image upload if provided
        photo_tmp = validated_data.pop('photo_tmp', None)

        if photo_tmp:
            uploaded_image_url = upload_file_to_digital_ocean(photo_tmp)
            validated_data['photo'] = uploaded_image_url  

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure string fields are cleaned properly
        for key in ['username', 'role', 'address', 'phone_number']:
            if isinstance(data.get(key), str):
                data[key] = data[key].strip()  

        return data




class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password','phone_number','address','city','postal_code', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def to_representation(self, instance):  # for password hidden from response
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"error": "Passwords do not match."})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {"email": "Email already exists."})

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {"username": "Username already exists."})

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data['identifier']
        password = data['password']

        # Find user either by username or email
        user = None
        if '@' in identifier and '.' in identifier:
            user = User.objects.filter(email=identifier).first()
        else:
            user = User.objects.filter(username=identifier).first()


        # If the user is not found, raise an error for identifier
        if not user:
            raise serializers.ValidationError({"identifier": "Invalid credentials. Please check your email or username."})

        # Check if the user is active
        if not user.is_active:
            raise serializers.ValidationError({"identifier": "Your account is not active. Please verify your email."})

        # Check password manually and raise an error for password
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Incorrect password. Please try again."})

        # Authenticate the user with the provided password if the account is active and verified
        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials. Please check your email or password.")

        return {"user": user}


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    def to_representation(self, instance):
        return {
            'access': instance.access_token,
            'refresh': instance.refresh_token,
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this email does not exist.")


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                "New password and confirmation password do not match.")
        return data


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                "New password and confirmation password do not match.")
        return data


class CustomUserAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'is_active']
