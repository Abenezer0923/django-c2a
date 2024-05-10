import random

def generate_numeric_otp():
    """
        generate otp with interval of 1000 and 9999 inclusive randomly
    """
    otp = random.randint(1000, 9999)
    return otp

