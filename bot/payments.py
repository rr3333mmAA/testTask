import uuid
from os import getenv

from dotenv import load_dotenv
from yookassa import Configuration, Payment


class YooKassa:
    def __init__(self, amount, description):
        load_dotenv()
        Configuration.account_id = getenv('YOOKASSA_ID')
        Configuration.secret_key = getenv('YOOKASSA_TOKEN')

        self.payment = Payment.create({
            "amount": {
                "value": f"{amount}.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/{getenv('BOT_USERNAME')}"
            },
            "capture": True,
            "description": f"{description}"
        }, uuid.uuid4())

    async def get_payment_url(self):
        return self.payment.confirmation.confirmation_url

    async def get_payment_status(self):
        return Payment.find_one(self.payment.id).status
