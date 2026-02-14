import random
from kavenegar import *

from RLT import settings


def generate_otp():
    return str(random.randint(100000, 999999))

def send_sms_to_user(phone, text):
    try:
        api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
        print(text)

        params = {
            'receptor': phone,
            'message': text,
        }

        response = api.sms_send(params)
        return response

    except APIException as e:
        print("Kavenegar API Error:", e)
        return None

    except HTTPException as e:
        print("Kavenegar HTTP Error:", e)
        return None

    except Exception as e:
        print("Unexpected SMS Error:", e)
        return None
