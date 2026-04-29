from __future__ import annotations
from typing import Any, Dict, Optional
import re


ALLOWED_TYPES = {"USER_SIGNUP", "PAYMENT", "FILE_UPLOAD"}


def _err(*msgs: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "message": "Event rejected",
        "data": None,
        "errors": list(msgs),
    }


def _ok(message: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "ok",
        "message": message,
        "data": data,
        "errors": [],
    }


def _is_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))


def handler(event: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not isinstance(event, dict):
        return _err("Event must be a dictionary")

    if "type" not in event:
        return _err("Missing event type")

    event_type = event["type"]

    if event_type not in ALLOWED_TYPES:
        return _err("Invalid event type")

    if event_type == "USER_SIGNUP":
        return handle_user_signup(event)
    if event_type == "PAYMENT":
        return handle_payment(event)
    if event_type == "FILE_UPLOAD":
        return handle_file_upload(event)

    return _err("Unhandled event type")


def handle_user_signup(event: Dict[str, Any]) -> Dict[str, Any]:
    if "user_id" not in event or not isinstance(event["user_id"], int):
        return _err("Invalid or missing user_id")

    if "email" not in event or not isinstance(event["email"], str):
        return _err("Invalid or missing email")

    if "plan" not in event or not isinstance(event["plan"], str):
        return _err("Invalid or missing plan")

    email = event["email"].lower()
    plan = event["plan"].lower()

    if not _is_email(email):
        return _err("Invalid email format")

    if plan not in {"free", "pro", "edu"}:
        return _err("Invalid plan")

    data = {
        "user_id": event["user_id"],
        "email": email,
        "plan": plan,
        "welcome_email_subject": f"Welcome to {plan} plan",
    }

    return _ok("User signup processed", data)


def handle_payment(event: Dict[str, Any]) -> Dict[str, Any]:
    if "payment_id" not in event or not isinstance(event["payment_id"], str):
        return _err("Invalid or missing payment_id")

    if "user_id" not in event or not isinstance(event["user_id"], int):
        return _err("Invalid or missing user_id")

    if "amount" not in event or not isinstance(event["amount"], (int, float)):
        return _err("Invalid or missing amount")

    if "currency" not in event or not isinstance(event["currency"], str):
        return _err("Invalid or missing currency")

    amount = float(event["amount"])

    if amount <= 0:
        return _err("Amount must be greater than 0")

    currency = event["currency"].upper()

    if currency not in {"BHD", "USD", "EUR"}:
        return _err("Invalid currency")

    amount = round(amount, 3)
    fee = round(amount * 0.02, 3)
    net_amount = round(amount - fee, 3)

    data = {
        "payment_id": event["payment_id"],
        "user_id": event["user_id"],
        "amount": amount,
        "currency": currency,
        "fee": fee,
        "net_amount": net_amount,
    }

    return _ok("Payment processed", data)


def handle_file_upload(event: Dict[str, Any]) -> Dict[str, Any]:
    if "file_name" not in event or not isinstance(event["file_name"], str):
        return _err("Invalid or missing file_name")

    if "size_bytes" not in event or not isinstance(event["size_bytes"], int):
        return _err("Invalid or missing size_bytes")

    if "bucket" not in event or not isinstance(event["bucket"], str):
        return _err("Invalid or missing bucket")

    if "uploader" not in event or not isinstance(event["uploader"], str):
        return _err("Invalid or missing uploader")

    if event["size_bytes"] < 0:
        return _err("size_bytes must be >= 0")

    file_name = event["file_name"].strip()
    bucket = event["bucket"].lower()
    uploader = event["uploader"].lower()

    if not _is_email(uploader):
        return _err("Invalid uploader email")

    size = event["size_bytes"]

    if size < 1_000_000:
        storage_class = "STANDARD"
    elif size < 50_000_000:
        storage_class = "STANDARD_IA"
    else:
        storage_class = "GLACIER"

    data = {
        "file_name": file_name,
        "size_bytes": size,
        "bucket": bucket,
        "uploader": uploader,
        "storage_class": storage_class,
    }

    return _ok("File upload processed", data)