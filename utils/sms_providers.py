import requests
from decouple import config
from .otp_generator import generate_numeric_otp


class PurposeSMS:
    def __init__(self):
        self.session  = requests.Session()
        # self.base_url = config("MESSAGES_BASE_URL")
        # self.sender    = config("MESSAGE_SENDER")

    @classmethod
    def format_phone(cls, phone):
        if phone is not None:
            phone = phone.replace(" ", "")
            phone = phone.replace("-", "")
            phone = phone.replace(".", "")
        return f"+2519{phone[-8:]}"

    def send_otp(
        self,
        to,
        post="is your verification code for China2Afrika",
       
    ):
        to = self.format_phone(to)
        to = self.format_phone(to)
        url = f"http://sms.purposeblacketh.com/api/general/send-sms/"
        otp = generate_numeric_otp()
        payload = {"phone":to,"text": f"{otp} {post}"}
        status_code=  requests.post(url,data=payload)
        
        return status_code,otp
        
        

    def send_sms(self, numbers: list, message: str):
        for to in numbers:
            url = "%s?from=%s&sender=%s&to=%s&message=%s" % (
                self.base_url,
                self.from_phone,
                self.sender,
                self.format_phone(to),
                message,
            )
            result = self.session.get(url, headers=self.headers)
            if result.status_code == 200:
                json = result.json()
                if json["acknowledge"] == "success":
                    return True, json.get("response")
                else:
                    return False, json.get("response")
            else:
                return False, result

