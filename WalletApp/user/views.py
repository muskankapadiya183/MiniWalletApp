from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, permissions
from .response_handler import ResponseHandler
from .models import User, Wallet, Transaction
from datetime import datetime
from django.utils import timezone
from django.db import transaction
import requests
from decimal import Decimal, ROUND_DOWN
from .pagination import TransactionListPagination
from rest_framework.generics import ListAPIView
from django.db.models import Q
from decouple import config 

EXCHANGE_API = config('EXCHANGE_API')

# Create your views here.

class AuthUserLoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    response_handler = ResponseHandler()
    
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                response_dict, status_code = self.response_handler.success(
                    data=serializer.data,
                    msg="User login successfully.",
                )
                return Response(
                    response_dict,
                    status=status_code,
                )
            else:
                response_dict, status_code = self.response_handler.error(
                    data=serializer.errors,
                    msg="Your username or password is wrong.",
                )
                return Response(
                    response_dict,
                    status=status_code,
                )
        except Exception as e:
            print(f"Exception in AuthUserLoginView: \n {e}")
            response_dict, status_code = self.response_handler.failure(
                data=None, error=None, msg="Something went wrong."
            )
            return Response(
                response_dict,
                status=status_code,
            )

class AuthUserRegisterView(APIView):
    serialize_class = RegisterSerializer
    permission_classes = [AllowAny]
    response_handler = ResponseHandler()

    def post(self, request):
        try:
            serializer = self.serialize_class(data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                response_dict, status_code = self.response_handler.success(
                    data=serializer.data,
                    msg="User Register successfully.",
                )
                return Response(
                    response_dict,
                    status=status_code,
                )
            else:
                response_dict, status_code = self.response_handler.error(
                    data=serializer.errors,
                    msg="Your username or password is wrong.",
                )
                return Response(
                    response_dict,
                    status=status_code,
                )
        except Exception as e:
            print(f"Exception in AuthUserRegisterView: \n {e}")
            response_dict, status_code = self.response_handler.error(
                msg=str(e),
            )
            return Response(
                response_dict,
                status=status_code,
            )

class WalletView(APIView):
    permission_classes = [IsAuthenticated]
    response_handler = ResponseHandler()
    serializer_class = WalletSerializer

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            serializer = self.serializer_class(wallet)
            response_dict, status_code = self.response_handler.success(
                data=serializer.data,
                msg="Wallet fetched successfully.",
            )
            return Response(response_dict, status=status_code)
        except Wallet.DoesNotExist:
            response_dict, status_code = self.response_handler.error(
                data=None, error="Wallet not found.", msg="Wallet not found."
            )
            return Response(response_dict, status=status_code)
        except Exception as e:
            print(f"Exception in WalletView: \n {e}")
            response_dict, status_code = self.response_handler.failure(
                data=None, error=str(e), msg="Something went wrong."
            )
            return Response(response_dict, status=status_code)

class TransferView(APIView):
    serialize_class = TransferSerializer
    permission_classes = [IsAuthenticated]
    response_handler = ResponseHandler()

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_exchange_rate(self, amount, from_currency, to_currency):
        if from_currency == to_currency:
            return Decimal("1.0")
        try:
            response = requests.get(f'{EXCHANGE_API}?amount={amount}&from={from_currency}&to={to_currency}')
            response.raise_for_status()
            rate = response.json()['rates'][to_currency]
            return Decimal(str(rate)) / Decimal(str(amount))
        except:
            raise Exception("Failed to fetch exchange rate")

    def post(self, request):
        serializer = self.serialize_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        receiver_email = serializer.validated_data['receiver_email']
        amount = Decimal(str(serializer.validated_data['amount']))
        from_currency = serializer.validated_data['from_currency'].upper()
        to_currency = serializer.validated_data['to_currency'].upper()

        try:
            receiver = User.objects.get(email=receiver_email)
            sender_wallet = Wallet.objects.get(user=request.user)
            receiver_wallet = Wallet.objects.get(user=receiver)

            # Convert wallet balances to Decimal before operations
            sender_usd_balance = Decimal(str(sender_wallet.usd_balance))
            sender_inr_balance = Decimal(str(sender_wallet.balance))
            receiver_usd_balance = Decimal(str(receiver_wallet.usd_balance))
            receiver_inr_balance = Decimal(str(receiver_wallet.balance))

            # Validate balance
            if from_currency == 'USD':
                if sender_wallet.usd_balance < amount:
                    response_dict, status_code = self.response_handler.error(
                        data=None, error={}, msg="Insufficient USD balance."
                    )
                    return Response(response_dict, status=status_code)
            else:
                if sender_wallet.balance < amount:
                    response_dict, status_code = self.response_handler.error(
                        data=None, error={}, msg=f"Insufficient {from_currency} balance."
                    )
                    return Response(response_dict, status=status_code)

            exchange_rate = self.get_exchange_rate(amount, from_currency, to_currency)
            converted_amount = (amount * exchange_rate).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

            with transaction.atomic():
                # Deduct from sender
                if from_currency == 'USD':
                    if sender_usd_balance < amount:
                        response_dict, status_code = self.response_handler.error(
                            data=None, error={}, msg="Insufficient USD balance."
                        )
                        return Response(response_dict, status=status_code)
                    sender_wallet.usd_balance = sender_usd_balance - amount
                else:
                    if sender_inr_balance < amount:
                        response_dict, status_code = self.response_handler.error(
                            data=None, error={}, msg=f"Insufficient {from_currency} balance."
                        )
                        return Response(response_dict, status=status_code)
                    sender_wallet.balance = sender_inr_balance - amount
                sender_wallet.save()

                # Credit to receiver
                if to_currency == 'USD':
                    receiver_wallet.usd_balance = receiver_usd_balance + converted_amount
                else:
                    receiver_wallet.balance = receiver_inr_balance + converted_amount
                receiver_wallet.save()

                ip_address = self.get_client_ip(request)

                # Log sender transaction
                Transaction.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    amount=amount,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    exchange_rate=exchange_rate,
                    transaction_type='SENT',
                    ip_address=ip_address
                )

                # Log receiver transaction
                Transaction.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    amount=converted_amount,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    exchange_rate=exchange_rate,
                    transaction_type='RECEIVED',
                    ip_address=ip_address
                )

            response_dict, status_code = self.response_handler.success(
                data={},
                msg="Transfer successfully.",
            )
            return Response(
                response_dict,
                status=status_code,
            )

        except User.DoesNotExist:
            response_dict, status_code = self.response_handler.error(
                data=None, error=str(e), msg="Receiver not found"
            )
            return Response(response_dict, status=status_code)
        except Wallet.DoesNotExist:
            response_dict, status_code = self.response_handler.error(
                data=None, error=str(e), msg="Wallet not found."
            )
            return Response(response_dict, status=status_code)
        except Exception as e:
            response_dict, status_code = self.response_handler.failure(
                data=None, error=str(e), 
            )
            return Response(response_dict, status=status_code)

class TransactionListView(ListAPIView): 
    permission_classes = (IsAuthenticated,)
    response_handler = ResponseHandler()
    serializer_class = TransactionListSerializer
    
    # Pagination settings
    pagination_class = TransactionListPagination
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = Transaction.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
            # Type Filtering 
            type_filter = self.request.query_params.get('type')
            if type_filter in ['sent', 'received']:
                queryset = queryset.filter(transaction_type=type_filter.upper())
            else:
                queryset = queryset

            # Date Filtering 
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            if date_from:
                try:
                    queryset = queryset.filter(created_at__gte=datetime.strptime(date_from, '%Y-%m-%d'))
                except ValueError:
                    response_dict, status_code = self.response_handler.error(
                        data=None, error=str(e), msg="Invalid date_from format."
                    )
                    return Response(response_dict, status=status_code)
            if date_to:
                try:
                    queryset = queryset.filter(created_at__lte=datetime.strptime(date_to, '%Y-%m-%d'))
                except ValueError:
                    response_dict, status_code = self.response_handler.error(
                        data=None, error=str(e), msg="Invalid date_from format."
                    )
                    return Response(response_dict, status=status_code)

            # Getting page and page_size dynamically from request query params
            page = request.query_params.get('page', 1)  # Default to page 1 if not provided
            per_page = request.query_params.get('per_page', 10)  # Default to 10 if not provided

            # Use pagination to limit the queryset
            page_size =  10
            # page_size = int(per_page) if per_page.isdigit() else 10
            paginator = self.pagination_class()
            paginator.page_size = page_size  # Override the default page size

            # Apply pagination
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                # If no pagination is needed (when queryset is small)
                serializer = self.get_serializer(queryset, many=True)
                response_dict, status_code = self.response_handler.success(
                    data=serializer.data,
                    msg="No pagination applied (all data fetched).",
                )
                return Response(response_dict, status=status_code)
        
        except Exception as e:
            print(f"Exception in TransactionListView List: \n {e}")
            response_dict, status_code = self.response_handler.failure(
                data=None, error=str(e), msg="Something went wrong."
            )
            return Response(response_dict, status=status_code)
