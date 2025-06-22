from django.contrib import admin
from .forms import *
from .models import User, Wallet, Transaction
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = User

    list_display = ('email', 'name','is_staff', 'is_active', 'email_verified',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'email_verified',)}),
        # ('Personal Info', {'fields': ('created_by',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'is_delete', 'email_verified')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, CustomUserAdmin)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "user", "balance", "usd_balance", "created_at", "updated_at"
    )

    class Meta:
        model = Wallet

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "sender",
        "receiver",
        "amount",
        "from_currency",
        "to_currency",
        "exchange_rate",
        "transaction_type",
        "ip_address",
        "created_at",
    )

    class Meta:
        model = Transaction