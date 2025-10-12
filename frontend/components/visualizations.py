"""Reusable visualization components using Plotly."""

from typing import Any, Dict, List, Optional, Union

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Custom Plotly theme colors
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "warning": "#d62728",
    "info": "#9467bd",
    "light": "#e0e0e0",
}


def get_plotly_template() -> Dict[str, Any]:
    """Get custom Plotly template."""
    return {
        "layout": {
            "font": {"family": "Arial, sans-serif", "size": 12},
            "plot_bgcolor": "#ffffff",
            "paper_bgcolor": "#ffffff",
            "margin": {"l": 40, "r": 40, "t": 60, "b": 40},
            "hovermode": "closest",
            "xaxis": {"showgrid": True, "gridcolor": "#e0e0e0"},
            "yaxis": {"showgrid": True, "gridcolor": "#e0e0e0"},
        }
    }


def create_bar_chart(
    data: Dict[str, Union[int, float]],
    title: str,
    x_label: str = "",
    y_label: str = "",
    color: str = COLORS["primary"],
    horizontal: bool = False,
) -> go.Figure:
    """
    Create a bar chart.

    Args:
        data: Dictionary mapping labels to values
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Bar color
        horizontal: Create horizontal bar chart

    Returns:
        Plotly Figure object
    """
    labels = list(data.keys())
    values = list(data.values())

    if horizontal:
        fig = go.Figure(data=[go.Bar(x=values, y=labels, marker_color=color, orientation="h")])
        fig.update_layout(xaxis_title=y_label, yaxis_title=x_label)
    else:
        fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=color)])
        fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)

    fig.update_layout(title=title, **get_plotly_template()["layout"])

    return fig


def create_pie_chart(
    data: Dict[str, Union[int, float]],
    title: str,
    colors: Optional[List[str]] = None,
) -> go.Figure:
    """
    Create a pie chart.

    Args:
        data: Dictionary mapping labels to values
        title: Chart title
        colors: Optional list of colors

    Returns:
        Plotly Figure object
    """
    labels = list(data.keys())
    values = list(data.values())

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors) if colors else None,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Value: %{value}<br>Percent: %{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(title=title, **get_plotly_template()["layout"])

    return fig


def create_line_chart(
    data: Dict[str, List[Any]],
    title: str,
    x_label: str = "",
    y_label: str = "",
) -> go.Figure:
    """
    Create a line chart.

    Args:
        data: Dictionary with 'x' and 'y' keys containing lists
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data.get("x", []),
            y=data.get("y", []),
            mode="lines+markers",
            line=dict(color=COLORS["primary"], width=2),
            marker=dict(size=8),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        **get_plotly_template()["layout"],
    )

    return fig


def create_kpi_card(
    label: str, value: str, delta: Optional[str] = None, delta_color: str = "normal"
) -> None:
    """
    Create a KPI card using Streamlit.

    Args:
        label: KPI label
        value: KPI value
        delta: Optional delta value
        delta_color: Color for delta ("normal", "inverse", "off")
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def create_gauge_chart(
    value: float, title: str, min_val: float = 0, max_val: float = 100
) -> go.Figure:
    """
    Create a gauge chart.

    Args:
        value: Current value
        title: Chart title
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Plotly Figure object
    """
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={"text": title},
            delta={"reference": (max_val - min_val) / 2},
            gauge={
                "axis": {"range": [min_val, max_val]},
                "bar": {"color": COLORS["primary"]},
                "steps": [
                    {"range": [min_val, max_val * 0.5], "color": COLORS["light"]},
                    {"range": [max_val * 0.5, max_val], "color": "#c0c0c0"},
                ],
                "threshold": {
                    "line": {"color": COLORS["warning"], "width": 4},
                    "thickness": 0.75,
                    "value": max_val * 0.9,
                },
            },
        )
    )

    fig.update_layout(**get_plotly_template()["layout"])

    return fig


def create_heatmap(
    data: List[List[float]],
    x_labels: List[str],
    y_labels: List[str],
    title: str,
    colorscale: str = "Blues",
) -> go.Figure:
    """
    Create a heatmap.

    Args:
        data: 2D array of values
        x_labels: X-axis labels
        y_labels: Y-axis labels
        title: Chart title
        colorscale: Color scale name

    Returns:
        Plotly Figure object
    """
    fig = go.Figure(
        data=go.Heatmap(
            z=data,
            x=x_labels,
            y=y_labels,
            colorscale=colorscale,
            hovertemplate="x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>",
        )
    )

    fig.update_layout(title=title, **get_plotly_template()["layout"])

    return fig

