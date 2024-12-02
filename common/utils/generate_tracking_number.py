import random
import string


def generate_tracking_number():
    # Generate a random alphanumeric tracking number
    letters = string.ascii_uppercase
    numbers = string.digits
    tracking_number = "".join(random.choices(letters + numbers, k=10))
    return tracking_number
