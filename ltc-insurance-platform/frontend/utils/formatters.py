"""Data formatting utilities for display."""

from typing import Optional, Any
from datetime import datetime, date


def format_currency(value: Optional[float], decimals: int = 2) -> str:
    """Format value as currency."""
    if value is None:
        return "N/A"
    try:
        num_value = float(value)
        return f"${num_value:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value: Optional[float], decimals: int = 1) -> str:
    """Format value as percentage."""
    if value is None:
        return "N/A"
    try:
        num_value = float(value)
        return f"{num_value:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(value)


def format_number(value: Optional[Any], decimals: int = 0) -> str:
    """Format value as number with thousands separator."""
    if value is None:
        return "N/A"
    try:
        num_value = float(value)
        if decimals == 0:
            return f"{int(num_value):,}"
        return f"{num_value:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def format_date(value: Optional[Any], format_str: str = "%Y-%m-%d") -> str:
    """Format date value."""
    if value is None:
        return "N/A"
    
    if isinstance(value, str):
        try:
            # Try parsing common date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.strftime(format_str)
                except ValueError:
                    continue
            return value
        except Exception:
            return value
    
    if isinstance(value, (datetime, date)):
        return value.strftime(format_str)
    
    return str(value)


def format_days(value: Optional[float]) -> str:
    """Format days value."""
    if value is None:
        return "N/A"
    try:
        num_value = float(value)
        return f"{int(num_value)} days"
    except (ValueError, TypeError):
        return str(value)


def get_status_color(status: str) -> str:
    """Get color for status badge."""
    status_colors = {
        "Approved": "green",
        "Denied": "red",
        "In Assessment": "orange",
        "Closed": "gray",
        "Revoked": "red",
        "Recovery": "blue",
        "Deceased": "gray",
        "Active": "green",
        "Lapsed": "red",
        "ACTIVE": "green",
        "LAPSED": "red",
    }
    return status_colors.get(status, "gray")


def format_decision_text(decision: Optional[str]) -> str:
    """Format decision text for display."""
    if decision is None:
        return "N/A"
    return decision.title()


def format_category_text(category: str) -> str:
    """Format category text."""
    category_map = {
        "Facility": "🏥 Facility",
        "Home Health": "🏠 Home Health",
        "Other": "📋 Other"
    }
    return category_map.get(category, category)


def format_ongoing_rate_month(value: Optional[int]) -> str:
    """Format ongoing rate month value."""
    if value is None:
        return "N/A"
    
    mapping = {
        0: "Initial Decision",
        1: "Ongoing",
        2: "Restoration of Benefits"
    }
    return mapping.get(value, f"Unknown ({value})")


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length."""
    if text is None:
        return "N/A"
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

