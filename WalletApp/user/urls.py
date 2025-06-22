from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenBlacklistView
from django.conf import settings
from .views import *
from . import views
urlpatterns = [

    # Token related urls.
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # Authentications API's URL
    path('register', AuthUserRegisterView.as_view(), name='register'),
    path('login', AuthUserLoginView.as_view(), name='login'),

    # Wallet API's URL
    path('wallet', WalletView.as_view(), name='wallet'),

    # Transfer API's URL
    path('transfer', TransferView.as_view(), name='transfer'),
    
    # Transaction API's URL
    path('transactions', TransactionListView.as_view(), name='transactions'),
]