
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .paymob import get_paymob_token, create_order, get_payment_key, card_payment
from order.models import Order
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from core.settings import *

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        paymob_token = get_paymob_token()

        amount_cents = int(order.total_price * 100)
        order_id = create_order(paymob_token, amount_cents)

        payment_token = get_payment_key(paymob_token, order_id, amount_cents)

        order.paymob_order_id = order_id
        order.save()

        iframe_url = card_payment(payment_token)

        return Response({'success': True, 'iframe_url': iframe_url})

    except Order.DoesNotExist:
        return Response({'success': False, 'error': 'order not found.'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


import requests

# Your Paymob API Key
PAYMOB_API_KEY1 = PAYMOB_API_KEY

# Function to transfer money to vendor
def transfer_to_vendor(vendor_card_number, amount_cents):
    """
    Transfer funds to a vendor using Paymob's Disbursements API.
    :param vendor_card_number: The vendor's card number.
    :param amount_cents: The amount to transfer in cents (e.g., 10000 for $100.00).
    :return: Response from Paymob API.
    """
    url = "https://accept.paymob.com/api/disbursements/payouts"

    headers = {
        "Authorization": f"Bearer {PAYMOB_API_KEY1}",
        "Content-Type": "application/json",
    }

    payload = {
        "amount": amount_cents,  # Amount in cents
        "currency": "EGP",       # Update this if you are transferring in a different currency
        "recipient": {
            "type": "card",         # Use "bank_account" for bank transfers
            "card_number": vendor_card_number,
        },
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Paymob Payout Error: {response.text}")


import json
from .paymob import calculate_hmac
import os


# Load environment variables from the .env file


# Get the HMAC_SECRET from the .env file
HMAC_SECRET = "CB8DD982B47F3C9BB17D5039D3A9F88C"

# Ensure SECRET_KEY is defined
if not HMAC_SECRET:
    raise ValueError("The HMAC_SECRET environment variable is not set in the .env file.")

@csrf_exempt
@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def payment_status_webhook(request):
    print("Hellllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllo")
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON format'}, status=400)

    received_hmac = request.GET.get('hmac', '')
    calculated_hmac = calculate_hmac(data, HMAC_SECRET)

    if calculated_hmac != received_hmac:
        print("HMAC verification failed .........................", calculated_hmac)
        # return Response({'error': 'HMAC verification failed'}, status=400)
    else:
        print("HMAC verified successfully .........................")
    return Response({'success': True})



@api_view(['GET'])
@permission_classes([AllowAny])
def payment_redirect(request):
    success = request.query_params.get('success')
    payment_status_str = request.GET.get('success')
    print ("Payment status ...........................", payment_status_str)
    transaction_id = request.GET.get('id')
    print ("Payment id ...........................", transaction_id)
    paymob_order_id  = request.GET.get('order')
    print ("Payment order id ...........................", paymob_order_id)
    payment_status = True if payment_status_str == 'true' else False
    try:
        order = Order.objects.get(paymob_order_id=paymob_order_id)
        order.is_paid = payment_status
        order.payment_status = 'Paid' if payment_status else 'Failed'
        order.payment_method='ONLINE_CARD'
        order.save()
    except Order.DoesNotExist:
        print("Order with paymob_order_id does not exist")
        return Response({'error': 'Order not found'}, status=404)
    
    if success == 'true':
        # return HttpResponseRedirect("http://localhost:5173/?message=Payment successful")
        # return HttpResponseRedirect("https://airiti.netlify.app/?message=Payment successful")
        print("done payment david")
        return Response({'message': 'Payment successful'}, status=200)
    else:
        # return HttpResponseRedirect("http://localhost:5173/?message=Payment failed")
        # return HttpResponseRedirect("https://airiti.netlify.app/?message=Payment failed")
        print("payment failed david")
        return Response({'message': 'Payment failed'}, status=400)