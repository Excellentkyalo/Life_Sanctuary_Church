# website/mpesa_utils.py
import requests
import base64
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class MpesaAPI:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.base_url = settings.MPESA_BASE_URL
        self.callback_url = settings.MPESA_CALLBACK_URL

    def get_access_token(self):
        """Generate OAuth Access Token"""
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
        if response.status_code == 200:
            return response.json().get('access_token')
        raise ImproperlyConfigured("Could not fetch M-Pesa access token")

    def get_password(self):
        """Generate Base64 encoded password for STK Push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        encoded = base64.b64encode(data_to_encode.encode()).decode('utf-8')
        return encoded, timestamp

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push"""
        access_token = self.get_access_token()
        password, timestamp = self.get_password()
        
        # Format phone number (remove +, ensure 254)
        phone = str(phone_number).replace('+', '')
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": f"{settings.BASE_URL}{self.callback_url}",
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        response = requests.post(url, json=payload, headers=headers)
        return response.json()