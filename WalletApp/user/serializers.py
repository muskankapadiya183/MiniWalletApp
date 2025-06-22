from .models import User, Transaction, Wallet
from rest_framework import serializers
import re
from rest_framework_simplejwt.tokens import RefreshToken
import time
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "name",
            "email"
        )
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    id = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def create(self, validated_date):
        pass
    def update(self, instance, validated_data):
        pass
    
    def validate_email(self, value):
        try:
            User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                _("This account doesn't exist. Please create a new account.")
            )
        return value

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid login credentials")
        try: 
            user_obj = User.objects.get(email=user.email)
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)
            update_last_login(None, user)
            validation = {
                'access': access_token,
                'refresh': refresh_token,
                'email': user.email,
                'name': user.name,
                'id': user.id,
            }
            return validation
        except:
            raise serializers.ValidationError("Invalid ")

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = (
            "name",
            "email",
            "password",
            "confirm_password",
        )
    def validate_email(self, value):
        if value:
            return value.lower()
        return value

    def validate(self, attrs):
        print("attrs: - ", attrs)
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        # validating password
        password_val = attrs["password"]
        regex_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?#&])[A-Za-z\d@$!%*?#&]{6,14}$"
        is_email_regex_match = re.match(regex_pattern, password_val)
        if not is_email_regex_match:
            raise serializers.ValidationError(
                {
                    "password": "Password Length must be 6-14 characters, at least 1 caps, 1 small, 1 special char, 1 number."
                }
            )
        return attrs 
    
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = super(RegisterSerializer, self).create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        # Create a wallet for the user
        Wallet.objects.create(user=user)
        return user

class TransferSerializer(serializers.Serializer):
    receiver_email = serializers.EmailField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    from_currency = serializers.CharField(max_length=3, default='INR')
    to_currency = serializers.CharField(max_length=3, default='INR')

class TransactionListSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    class Meta:
        model = Transaction
        fields = (
            'id', 'sender', 'receiver', 'amount', 'from_currency', 'to_currency', 'exchange_rate', 'transaction_type', 'created_at'
        )

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = (
            "user",
            "balance",
            "usd_balance",
        )
    