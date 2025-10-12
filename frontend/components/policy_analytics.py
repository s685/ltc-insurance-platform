"""Policy analytics component."""

from typing import Optional
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from services.api_client import APIClient, PolicyMetrics
from utils.formatters import (
    format_currency,
    format_number,
    format_percentage,
)
from .visualizations import (
    create_bar_chart,
    create_gauge_chart,
    create_kpi_card,
    create_pie_chart,
)


def fetch_policy_data(
    api_client: APIClient,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> tuple[PolicyMetrics, list]:
    """Fetch policy data from API."""
    metrics = api_client.get_policy_metrics(start_date, end_date)
    policies_list = api_client.list_policies(limit=50)
    return metrics, policies_list


def render_policy_analytics(
    api_client: APIClient,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> None:
    """
    Render policy analytics dashboard.

    Args:
        api_client: API client instance
        start_date: Optional start date filter
        end_date: Optional end date filter
    """
    st.header("📊 Policy Analytics Dashboard")

    # Add loading state
    with st.spinner("Loading policy data..."):
        try:
            metrics, policies_list = fetch_policy_data(api_client, start_date, end_date)
        except Exception as e:
            st.error(f"Failed to load policy data: {str(e)}")
            return

    # KPI Row
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        create_kpi_card(
            "Total Policies",
            format_number(metrics.total_policies),
        )

    with col2:
        create_kpi_card(
            "Active Policies",
            format_number(metrics.active_policies),
        )

    with col3:
        create_kpi_card(
            "Lapse Rate",
            format_percentage(metrics.lapse_rate),
        )

    with col4:
        create_kpi_card(
            "Avg Insured Age",
            f"{metrics.avg_insured_age:.1f} years",
        )

    # Second KPI Row
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        create_kpi_card(
            "Total Premium",
            format_currency(metrics.total_premium),
        )

    with col6:
        create_kpi_card(
            "Avg Premium",
            format_currency(metrics.avg_premium),
        )

    with col7:
        create_kpi_card(
            "Avg Benefit",
            format_currency(metrics.avg_benefit),
        )

    with col8:
        create_kpi_card(
            "Lapsed Policies",
            format_number(metrics.lapsed_policies),
        )

    st.markdown("---")

    # Charts Row
    st.subheader("Policy Distribution Analysis")

    col_left, col_middle, col_right = st.columns(3)

    with col_left:
        # Policy Status Distribution
        status_data = {
            "Active": metrics.active_policies,
            "Lapsed": metrics.lapsed_policies,
            "Terminated": metrics.terminated_policies,
        }

        fig_status = create_pie_chart(
            status_data,
            "Policies by Status",
            colors=["#2ca02c", "#ff7f0e", "#d62728"],
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col_middle:
        # Policy Type Distribution
        if metrics.policy_type_distribution:
            fig_types = create_bar_chart(
                metrics.policy_type_distribution,
                "Policies by Type",
                y_label="Count",
                color="#1f77b4",
            )
            st.plotly_chart(fig_types, use_container_width=True)
        else:
            st.info("No policy type data available.")

    with col_right:
        # Lapse Rate Gauge
        lapse_rate_pct = metrics.lapse_rate * 100
        fig_gauge = create_gauge_chart(
            lapse_rate_pct,
            "Lapse Rate (%)",
            min_val=0,
            max_val=20,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("---")

    # Premium Analysis
    st.subheader("Premium Analysis")

    prem_col1, prem_col2 = st.columns(2)

    with prem_col1:
        # Calculate annual premium
        annual_premium = float(metrics.total_premium) * 12
        monthly_avg = float(metrics.avg_premium)

        premium_breakdown = {
            "Monthly Total": float(metrics.total_premium),
            "Annual Total": annual_premium,
        }

        fig_premium = create_bar_chart(
            premium_breakdown,
            "Premium Revenue",
            y_label="Amount ($)",
            color="#9467bd",
        )
        st.plotly_chart(fig_premium, use_container_width=True)

    with prem_col2:
        # Coverage ratio analysis
        avg_coverage_ratio = (
            float(metrics.avg_benefit) / float(metrics.avg_premium)
            if float(metrics.avg_premium) > 0
            else 0
        )

        st.metric("Average Coverage Ratio", f"{avg_coverage_ratio:.2f}x")

        st.info(
            f"""
            **Premium Insights**
            - Average monthly premium: {format_currency(metrics.avg_premium)}
            - Average daily benefit: {format_currency(metrics.avg_benefit)}
            - Coverage ratio indicates benefit multiplier vs. premium
            """
        )

    st.markdown("---")

    # Recent Policies Table
    st.subheader("Recent Policies")

    if policies_list:
        # Convert to DataFrame for display
        policies_data = []
        for policy in policies_list[:20]:  # Show top 20
            policies_data.append(
                {
                    "Policy ID": policy.policy_id[:8] + "...",
                    "Policy Number": policy.policy_number,
                    "Type": policy.policy_type,
                    "Status": policy.status,
                    "Insured Age": policy.insured_age,
                    "State": policy.insured_state,
                    "Premium": format_currency(policy.premium_amount),
                    "Benefit": format_currency(policy.benefit_amount),
                    "Issue Date": policy.issue_date.strftime("%Y-%m-%d"),
                }
            )

        df = pd.DataFrame(policies_data)

        # Add status color coding
        def highlight_status(row):
            if row["Status"] == "ACTIVE":
                return ["background-color: #d4edda"] * len(row)
            elif row["Status"] == "LAPSED":
                return ["background-color: #fff3cd"] * len(row)
            elif row["Status"] == "TERMINATED":
                return ["background-color: #f8d7da"] * len(row)
            else:
                return [""] * len(row)

        st.dataframe(
            df.style.apply(highlight_status, axis=1),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No policy data available.")

    # Additional Insights
    st.markdown("---")
    st.subheader("Portfolio Health")

    health_col1, health_col2, health_col3 = st.columns(3)

    with health_col1:
        retention_rate = 1 - metrics.lapse_rate
        st.info(
            f"""
            **Retention Metrics**
            - Retention rate: {format_percentage(retention_rate)}
            - Active policies: {format_number(metrics.active_policies)}
            - Lapsed policies: {format_number(metrics.lapsed_policies)}
            """
        )

    with health_col2:
        st.info(
            f"""
            **Demographics**
            - Average insured age: {metrics.avg_insured_age:.1f} years
            - Total active policyholders: {format_number(metrics.active_policies)}
            - Policy type diversity: {len(metrics.policy_type_distribution)} types
            """
        )

    with health_col3:
        monthly_revenue = float(metrics.total_premium)
        annual_revenue = monthly_revenue * 12

        st.info(
            f"""
            **Revenue Metrics**
            - Monthly premium revenue: {format_currency(monthly_revenue)}
            - Annual premium revenue: {format_currency(annual_revenue)}
            - Revenue per active policy: {format_currency(monthly_revenue / metrics.active_policies if metrics.active_policies > 0 else 0)}
            """
        )

