import random
import string

def generate_confirm_token(length=6):
    chars = string.ascii_uppercase + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(chars, k=length))

