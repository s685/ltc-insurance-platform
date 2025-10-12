"""Claims dashboard component."""

from typing import Optional
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from services.api_client import APIClient, ClaimSummary
from utils.formatters import (
    format_currency,
    format_number,
    format_percentage,
)
from .visualizations import (
    create_bar_chart,
    create_kpi_card,
    create_pie_chart,
)


def fetch_claims_data(
    api_client: APIClient,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> tuple[ClaimSummary, list]:
    """Fetch claims data from API."""
    summary = api_client.get_claims_summary(start_date, end_date)
    claims_list = api_client.list_claims(limit=50)
    return summary, claims_list


def render_claims_dashboard(
    api_client: APIClient,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> None:
    """
    Render claims analytics dashboard.

    Args:
        api_client: API client instance
        start_date: Optional start date filter
        end_date: Optional end date filter
    """
    st.header("📋 Claims Analytics Dashboard")

    # Add loading state
    with st.spinner("Loading claims data..."):
        try:
            summary, claims_list = fetch_claims_data(api_client, start_date, end_date)
        except Exception as e:
            st.error(f"Failed to load claims data: {str(e)}")
            return

    # KPI Row
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_kpi_card(
            "Total Claims",
            format_number(summary.total_claims),
        )

    with col2:
        create_kpi_card(
            "Approval Rate",
            format_percentage(summary.approval_rate),
        )

    with col3:
        create_kpi_card(
            "Avg Processing Time",
            f"{summary.avg_processing_days:.1f} days",
        )

    with col4:
        create_kpi_card(
            "Total Claim Amount",
            format_currency(summary.total_claim_amount),
        )

    # Second KPI Row
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        create_kpi_card(
            "Approved Claims",
            format_number(summary.approved_claims),
        )

    with col6:
        create_kpi_card(
            "Denied Claims",
            format_number(summary.denied_claims),
        )

    with col7:
        create_kpi_card(
            "Pending Claims",
            format_number(summary.pending_claims),
        )

    with col8:
        create_kpi_card(
            "Avg Claim Amount",
            format_currency(summary.avg_claim_amount),
        )

    st.markdown("---")

    # Charts Row
    st.subheader("Claims Analysis")

    col_left, col_right = st.columns(2)

    with col_left:
        # Claims by Status
        status_data = {
            "Approved": summary.approved_claims,
            "Denied": summary.denied_claims,
            "Pending": summary.pending_claims,
        }

        fig_status = create_pie_chart(
            status_data,
            "Claims Distribution by Status",
            colors=["#2ca02c", "#d62728", "#ff7f0e"],
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right:
        # Claims Amount Comparison
        amount_data = {
            "Total Claimed": float(summary.total_claim_amount),
            "Total Approved": float(summary.total_approved_amount),
            "Total Paid": float(summary.total_paid_amount),
        }

        fig_amounts = create_bar_chart(
            amount_data,
            "Claim Amounts Comparison",
            y_label="Amount ($)",
            color="#1f77b4",
        )
        st.plotly_chart(fig_amounts, use_container_width=True)

    st.markdown("---")

    # Recent Claims Table
    st.subheader("Recent Claims")

    if claims_list:
        # Convert to DataFrame for display
        claims_data = []
        for claim in claims_list[:20]:  # Show top 20
            claims_data.append(
                {
                    "Claim ID": claim.claim_id[:8] + "...",
                    "Claim Number": claim.claim_number,
                    "Status": claim.status,
                    "Type": claim.claim_type,
                    "Submission Date": claim.submission_date.strftime("%Y-%m-%d"),
                    "Claim Amount": format_currency(claim.claim_amount),
                    "Approved Amount": (
                        format_currency(claim.approved_amount)
                        if claim.approved_amount
                        else "N/A"
                    ),
                }
            )

        df = pd.DataFrame(claims_data)

        # Add status color coding
        def highlight_status(row):
            if row["Status"] in ["APPROVED", "PAID"]:
                return ["background-color: #d4edda"] * len(row)
            elif row["Status"] == "DENIED":
                return ["background-color: #f8d7da"] * len(row)
            else:
                return ["background-color: #fff3cd"] * len(row)

        st.dataframe(
            df.style.apply(highlight_status, axis=1),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No claims data available.")

    # Additional Insights
    st.markdown("---")
    st.subheader("Insights")

    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.info(
            f"""
            **Claims Processing Performance**
            - Average processing time: {summary.avg_processing_days:.1f} days
            - Approval rate: {format_percentage(summary.approval_rate)}
            - {summary.pending_claims} claims currently in review
            """
        )

    with insight_col2:
        approval_amount_rate = (
            float(summary.total_approved_amount / summary.total_claim_amount)
            if summary.total_claim_amount > 0
            else 0
        )
        st.info(
            f"""
            **Financial Summary**
            - Total claims submitted: {format_currency(summary.total_claim_amount)}
            - Amount approval rate: {format_percentage(approval_amount_rate)}
            - Total paid out: {format_currency(summary.total_paid_amount)}
            """
        )

