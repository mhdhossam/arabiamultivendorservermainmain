import base64
import hashlib
from datetime import datetime


def generate_sku(product):
    # Concatenate the selected fields
    fields = [
        product.name,
        product.brand.name,
        str(datetime.now()),
    ]  # Add more fields if needed
    concatenated_string = "".join(fields)

    # Apply cryptographic hash function
    hash_value = hashlib.sha256(concatenated_string.encode()).digest()

    # Convert hash value to unique identifier format
    converted_hash = base64.urlsafe_b64encode(hash_value).decode()

    # Take a subset as the SKU
    sku = converted_hash[:16]

    return sku
