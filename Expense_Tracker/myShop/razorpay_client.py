"""
Thin wrapper around the razorpay SDK. Keeps SDK quirks (e.g. amount in paise,
HMAC signature format) out of the views.
"""

import hashlib
import hmac
import razorpay
from django.conf import settings


def _client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def create_order(amount_rupees, receipt):
    """
    Creates an order on Razorpay's side. Returns the razorpay_order_id (str).
    `amount_rupees` is in INR — converted to paise internally.
    """
    amount_paise = int(round(float(amount_rupees) * 100))
    order = _client().order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'receipt': receipt,
        'payment_capture': 1,  # auto-capture on success
    })
    return order['id']


def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verifies the signature returned by Razorpay after a successful payment.
    Returns True if valid, False otherwise.
    """
    try:
        _client().utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False


def verify_webhook_signature(body_bytes, signature_header):
    """
    Verifies the signature on incoming webhook payloads using the webhook
    secret set in the Razorpay dashboard.
    """
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    if not secret:
        return False
    expected = hmac.new(
        key=secret.encode('utf-8'),
        msg=body_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header or '')