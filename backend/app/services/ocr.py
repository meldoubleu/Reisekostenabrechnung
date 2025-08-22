from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from pathlib import Path
from typing import Optional
from datetime import datetime
import re


def extract_text_from_file(file_path: str) -> str:
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        images = convert_from_path(file_path)
        text = "\n".join(pytesseract.image_to_string(img) for img in images)
        return text
    else:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img)


_amount_re = re.compile(r"(?<!\d)(\d+[\.,]\d{2})\s?(EUR|€|USD|CHF)?", re.IGNORECASE)
_date_re = re.compile(r"(\d{2}[\./-]\d{2}[\./-]\d{2,4})")


def simple_parse(text: str) -> dict:
    amount = None
    currency = None
    date = None
    merchant = None

    amt_match = _amount_re.search(text)
    if amt_match:
        raw = amt_match.group(1).replace(",", ".")
        try:
            amount = float(raw)
        except ValueError:
            amount = None
        cur = amt_match.group(2)
        if cur:
            currency = cur.replace("€", "EUR").upper()

    date_match = _date_re.search(text)
    if date_match:
        ds = date_match.group(1).replace("/", ".").replace("-", ".")
        try:
            date = datetime.strptime(ds, "%d.%m.%Y")
        except ValueError:
            try:
                date = datetime.strptime(ds, "%d.%m.%y")
            except ValueError:
                date = None

    # merchant heuristic: first line
    first_line = text.strip().splitlines()[0] if text.strip().splitlines() else None
    merchant = first_line[:255] if first_line else None

    return {
        "amount": amount,
        "currency": currency,
        "date": date,
        "merchant": merchant,
    }
