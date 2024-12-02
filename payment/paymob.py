import requests
from core.settings import PAYMOB_API_KEY, PAYMOB_INTEGRATION_ID
import hmac
import hashlib


def get_paymob_token():
    url = "https://accept.paymob.com/api/auth/tokens"
    data = {"api_key": PAYMOB_API_KEY}
    response = requests.post(url, json=data)
    return response.json().get('token')

def create_order(token, amount_cents):
    url = "https://accept.paymob.com/api/ecommerce/orders"
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "amount_cents": amount_cents,
        "currency": "EGP",
        "items": []
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json().get('id')

def get_payment_key(token, order_id, amount_cents):
    url = "https://accept.paymob.com/api/acceptance/payment_keys"
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        "amount_cents": amount_cents,
        "currency": "EGP",
        "order_id": order_id,
        "billing_data": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "phone_number": "+201011234567",
            "apartment": "NA",
            "floor": "NA",
            "street": "NA",
            "building": "NA",
            "city": "Cairo",
            "country": "EG",
            "state": "NA"
        },
        "integration_id": PAYMOB_INTEGRATION_ID
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json().get('token')


# Usage
def card_payment(payment_token):
    iframe_url = f'https://accept.paymob.com/api/acceptance/iframes/869644?payment_token={payment_token}'
    return iframe_url


def calculate_hmac(data, hmac_secret):
    
    # print ('data from paymob..........................................', data)
    """
    Function to calculate HMAC for the received data
    :param data: Dictionary of received data
    :param hmac_secret: The secret key used for HMAC calculation
    :return: Calculated HMAC in hex (lowercase)
    """
    # The order of keys that should be used for HMAC calculation
    hmac_keys = [
        'amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction', 
        'id', 'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded', 
        'is_standalone_payment', 'is_voided', 'order', 'owner', 'pending', 'source_data.pan', 
        'source_data.sub_type', 'source_data.type', 'success'
    ]

    # Extract values from nested dictionaries
    extracted_data = {
    "amount_cents": data["obj"]["amount_cents"],
    "created_at": data["obj"]["created_at"],
    "currency": data["obj"]["currency"],
    "error_occured": data["obj"]["error_occured"],
    "has_parent_transaction": data["obj"]["has_parent_transaction"],
    "id": data["obj"]["id"],
    "integration_id": data["obj"]["integration_id"],
    "is_3d_secure": data["obj"]["is_3d_secure"],
    "is_auth": data["obj"]["is_auth"],
    "is_capture": data["obj"]["is_capture"],
    "is_refunded": data["obj"]["is_refunded"],
    "is_standalone_payment": data["obj"]["is_standalone_payment"],
    "is_voided": data["obj"]["is_voided"],
    "order_id": data["obj"]["order"]["id"],
    "owner": data["obj"]["owner"],
    "pending": data["obj"]["pending"],
    "source_data_pan": data["obj"]["source_data"]["pan"],
    "source_data_sub_type": data["obj"]["source_data"]["sub_type"],
    "source_data_type": data["obj"]["source_data"]["type"],
    "success": data["obj"]["success"]
}
    # Concatenate the extracted data into a single string
    concatenated_values  = ''.join([str(value).lower() if isinstance(value, bool) else str(value) for value in extracted_data.values()])
    # Print the concatenated string
    print("*",concatenated_values )

    # Calculate HMAC using SHA512
    calculated_hmac = hmac.new(
        hmac_secret.encode('utf-8'),
        concatenated_values.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()

    return calculated_hmac