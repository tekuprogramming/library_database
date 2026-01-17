from datetime import datetime
from tkinter import messagebox

def validate_date(date_str):
    """
    Validates that the input string is a valid date in YYYY-MM-DD format.
    Returns the same string if valid, or None if empty.
    Shows a messagebox if invalid.

    :param date_str: str, the date input to validate
    :return: str or None
    """
    if not date_str:
        return None  # allow empty input
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")  # normalize format
    except ValueError:
        messagebox.showerror("Invalid Date", "Please enter a valid date in format YYYY-MM-DD.")
        return None

def validate_binding(binding):
    """
    Validates that the provided book binding is one of the allowed types.

    Allowed values:
    - "hardcover"
    - "paperback"
    - "ebook"

    :param binding: str, the binding type to validate
    :raises ValueError: if the binding is not in the allowed set
    """
    allowed = {"hardcover", "paperback", "ebook"}
    if binding not in allowed:
        raise ValueError("Invalid binding")

def validate_rating(value):
    """
    Validates and converts a rating input to a float between 0 and 5.

    - Empty or None input returns None (rating not provided)
    - Non-empty input is converted to float
    - Raises ValueError if the rating is outside the range 0–5

    :param value: str or float, the rating to validate
    :return: float or None, the validated rating
    :raises ValueError: if the rating is outside 0–5
    """
    if not value:
        return None
    r = float(value)
    if not (0 <= r <= 5):
        raise ValueError("Rating 0–5")

    return r
