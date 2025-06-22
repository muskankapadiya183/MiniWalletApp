import uuid
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import CustomUserManager
from django.utils import timezone
# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, verbose_name='Public identifier')
    name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=500)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    update_on = models.DateTimeField(auto_now=True, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'user'

    def __str__(self):
        return self.email or ''

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.00)
    usd_balance = models.FloatField(default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallet'

    def __str__(self):
        return f"{self.user.name}'s Wallet"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
    )
    
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.FloatField()
    from_currency = models.CharField(max_length=3, default='INR')
    to_currency = models.CharField(max_length=3, default='INR')
    exchange_rate = models.FloatField(null=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transaction'

    def __str__(self):
        return f"{self.sender.name} to {self.receiver.name}: {self.amount} {self.from_currency}"