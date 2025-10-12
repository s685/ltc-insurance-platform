"""Data formatting utilities."""

from typing import Optional, Union
from datetime import date, datetime
from decimal import Decimal


def format_currency(amount: Union[Decimal, float, int]) -> str:
    """
    Format amount as currency.

    Args:
        amount: Amount to format

    Returns:
        Formatted currency string
    """
    if isinstance(amount, Decimal):
        amount = float(amount)

    return f"${amount:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage.

    Args:
        value: Value between 0 and 1
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """
    Format number with thousands separator.

    Args:
        value: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted number string
    """
    if decimals == 0:
        return f"{int(value):,}"
    else:
        return f"{value:,.{decimals}f}"


def format_date(dt: Union[date, datetime, None]) -> str:
    """
    Format date or datetime.

    Args:
        dt: Date or datetime to format

    Returns:
        Formatted date string
    """
    if dt is None:
        return "N/A"

    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M")
    else:
        return dt.strftime("%Y-%m-%d")

