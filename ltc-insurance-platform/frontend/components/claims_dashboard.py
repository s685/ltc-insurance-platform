"""Claims dashboard component with full analytics."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List
from datetime import date, datetime

from services.api_client import APIClient
from utils.formatters import (
    format_currency, format_percentage, format_number,
    format_days, get_status_color, format_decision_text,
    format_ongoing_rate_month
)


def render_claims_dashboard(api_client: APIClient):
    """Render claims analytics dashboard."""
    st.title("📊 Claims Analytics Dashboard")
    
    # Sidebar filters
    st.sidebar.header("Claims Filters")
    
    carrier_name = st.sidebar.text_input(
        "Carrier Name",
        value="Acme Insurance Co",
        help="Filter by carrier name"
    )
    
    report_end_dt = st.sidebar.date_input(
        "Report End Date",
        value=date(2024, 10, 31),
        help="Select report end date for snapshot"
    )
    
    # Decision types multiselect
    all_decision_types = [
        "In Assessment", "Approved", "Denied", 
        "Closed", "Revoked", "Recovery", "Deceased"
    ]
    decision_types = st.sidebar.multiselect(
        "Decision Types",
        options=all_decision_types,
        default=None,
        help="Filter by decision types (leave empty for all)"
    )
    
    # Ongoing rate month filter
    ongoing_rate_options = {
        "All": None,
        "Initial Decision (0)": [0],
        "Ongoing (1)": [1],
        "Restoration (2)": [2],
        "Initial + Ongoing": [0, 1],
        "Initial + Restoration": [0, 2]
    }
    ongoing_selection = st.sidebar.selectbox(
        "Ongoing Rate Month",
        options=list(ongoing_rate_options.keys()),
        index=0
    )
    ongoing_rate_months = ongoing_rate_options[ongoing_selection]
    
    # Category filter
    categories = st.sidebar.multiselect(
        "Categories",
        options=["Facility", "Home Health", "Other"],
        default=None,
        help="Filter by care category"
    )
    
    # Fetch data button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    try:
        # Fetch claims summary (using working endpoint)
        with st.spinner("Loading claims data..."):
            summary = api_client.get_claims_summary(
                carrier_name=carrier_name,
                report_end_dt=report_end_dt
            )
        
        if not summary:
            st.warning("No claims data available for the selected filters.")
            return
        
        # Build insights from summary data
        decision_breakdown = {
            "Approved": summary.get("approved_claims", 0),
            "Denied": summary.get("denied_claims", 0),
            "In Assessment": summary.get("in_assessment_claims", 0)
        }
        category_breakdown = {
            "Facility": summary.get("facility_claims", 0),
            "Home Health": summary.get("home_health_claims", 0),
            "Other": summary.get("other_claims", 0)
        }
        retro_analysis = {
            "total_retro_claims": summary.get("total_retro_claims", 0),
            "retro_percentage": summary.get("retro_percentage", 0.0)
        }
        
        # KPI Cards
        st.header("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Claims",
                format_number(summary.get("total_claims", 0)),
                help="Total number of claims"
            )
        
        with col2:
            approval_rate = summary.get("approval_rate", 0)
            st.metric(
                "Approval Rate",
                format_percentage(approval_rate),
                help="Percentage of approved claims"
            )
        
        with col3:
            avg_tat = summary.get("avg_processing_time_days", 0)
            st.metric(
                "Avg Processing Time",
                format_days(avg_tat),
                help="Average turnaround time"
            )
        
        with col4:
            retro_pct = summary.get("retro_percentage", 0)
            st.metric(
                "Retro Claims %",
                format_percentage(retro_pct),
                delta=f"{summary.get('total_retro_claims', 0)} claims",
                help="Percentage of retroactive claims"
            )
        
        # Additional KPIs
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                "Approved",
                format_number(summary.get("approved_claims", 0)),
                delta=None,
                delta_color="normal"
            )
        
        with col6:
            st.metric(
                "Denied",
                format_number(summary.get("denied_claims", 0)),
                delta=None,
                delta_color="inverse"
            )
        
        with col7:
            st.metric(
                "In Assessment",
                format_number(summary.get("in_assessment_claims", 0))
            )
        
        with col8:
            st.metric(
                "Initial Decisions",
                format_number(summary.get("initial_decisions", 0))
            )
        
        # Charts Row 1
        st.header("Claims Analysis")
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Decision breakdown pie chart
            if decision_breakdown:
                st.subheader("Decision Distribution")
                fig_decision = go.Figure(data=[go.Pie(
                    labels=list(decision_breakdown.keys()),
                    values=list(decision_breakdown.values()),
                    hole=0.3,
                    marker=dict(
                        colors=['#00CC96', '#EF553B', '#FFA15A', '#636EFA', '#AB63FA', '#19D3F3', '#FF6692']
                    )
                )])
                fig_decision.update_layout(height=350)
                st.plotly_chart(fig_decision)
            else:
                st.info("No decision breakdown available")
        
        with col_right:
            # Category breakdown
            if category_breakdown:
                st.subheader("Category Distribution")
                fig_category = go.Figure(data=[go.Bar(
                    x=list(category_breakdown.keys()),
                    y=list(category_breakdown.values()),
                    marker_color=['#636EFA', '#00CC96', '#FFA15A']
                )])
                fig_category.update_layout(
                    height=350,
                    xaxis_title="Category",
                    yaxis_title="Number of Claims"
                )
                st.plotly_chart(fig_category)
            else:
                st.info("No category breakdown available")
        
        # Charts Row 2
        col_left2, col_right2 = st.columns(2)
        
        with col_left2:
            # Ongoing rate month breakdown
            st.subheader("Decision Type Breakdown")
            ongoing_data = {
                "Initial": summary.get("initial_decisions", 0),
                "Ongoing": summary.get("ongoing_decisions", 0),
                "Restoration": summary.get("restoration_decisions", 0)
            }
            fig_ongoing = go.Figure(data=[go.Bar(
                x=list(ongoing_data.keys()),
                y=list(ongoing_data.values()),
                marker_color=['#AB63FA', '#19D3F3', '#FF6692'],
                text=list(ongoing_data.values()),
                textposition='auto'
            )])
            fig_ongoing.update_layout(
                height=350,
                xaxis_title="Decision Type",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_ongoing)
        
        with col_right2:
            # Retro analysis
            if retro_analysis and retro_analysis.get("total_retro_claims", 0) > 0:
                st.subheader("Retro Claims Analysis")
                retro_data = {
                    "Facility": retro_analysis.get("total_retro_facilities", 0) or 0,
                    "Home Health": retro_analysis.get("total_retro_home_health", 0) or 0,
                    "Other": retro_analysis.get("total_retro_other", 0) or 0
                }
                fig_retro = go.Figure(data=[go.Bar(
                    x=list(retro_data.keys()),
                    y=list(retro_data.values()),
                    marker_color=['#EF553B', '#00CC96', '#FFA15A']
                )])
                fig_retro.update_layout(
                    height=350,
                    xaxis_title="Category",
                    yaxis_title="Retro Claims"
                )
                st.plotly_chart(fig_retro)
                
                avg_retro_months = retro_analysis.get("avg_retro_months", 0)
                if avg_retro_months:
                    # Convert to float if it's a string
                    try:
                        avg_retro_val = float(avg_retro_months) if avg_retro_months else 0
                        st.info(f"Average Retro Months: {avg_retro_val:.1f}")
                    except (ValueError, TypeError):
                        st.info(f"Average Retro Months: {avg_retro_months}")
            else:
                st.info("No retroactive claims in this period")
        
        # Recent Claims Table
        st.header("Recent Claims")
        
        # Fetch claims list
        claims_list = api_client.get_claims(
            carrier_name=carrier_name,
            report_end_dt=report_end_dt,
            decision_types=decision_types if decision_types else None,
            ongoing_rate_months=ongoing_rate_months,
            categories=categories if categories else None,
            limit=50
        )
        
        if claims_list:
            # Convert to DataFrame
            df = pd.DataFrame(claims_list)
            
            # Select and format columns
            display_columns = [
                'policy_number', 'claimantname', 'decision',
                'certificationdate', 'ongoing_rate_month',
                'rfb_process_to_decision_tat', 'retro_months'
            ]
            
            # Filter existing columns
            display_columns = [col for col in display_columns if col in df.columns]
            df_display = df[display_columns].copy()
            
            # Rename columns
            column_rename = {
                'policy_number': 'Policy Number',
                'claimantname': 'Claimant Name',
                'decision': 'Decision',
                'certificationdate': 'Certification Date',
                'ongoing_rate_month': 'Type',
                'rfb_process_to_decision_tat': 'TAT (Days)',
                'retro_months': 'Retro Months'
            }
            df_display.rename(columns=column_rename, inplace=True)
            
            # Format columns
            if 'Type' in df_display.columns:
                df_display['Type'] = df_display['Type'].apply(format_ongoing_rate_month)
            
            # Display with color coding
            st.dataframe(
                df_display,
                height=400
            )
            
            # Download button
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download Claims Data (CSV)",
                data=csv,
                file_name=f"claims_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No claims found matching the selected filters.")
    
    except Exception as e:
        st.error(f"Error loading claims data: {str(e)}")
        st.exception(e)

