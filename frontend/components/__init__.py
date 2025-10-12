"""UI components module."""

from .claims_dashboard import render_claims_dashboard
from .policy_analytics import render_policy_analytics
from .visualizations import (
    create_bar_chart,
    create_line_chart,
    create_pie_chart,
    create_kpi_card,
)

__all__ = [
    "render_claims_dashboard",
    "render_policy_analytics",
    "create_bar_chart",
    "create_line_chart",
    "create_pie_chart",
    "create_kpi_card",
]

