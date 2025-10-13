"""Policy analytics dashboard component."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional
from datetime import datetime

from services.api_client import APIClient
from utils.formatters import (
    format_currency, format_percentage, format_number,
    format_date, get_status_color
)


def render_policy_dashboard(api_client: APIClient):
    """Render policy analytics dashboard."""
    st.title("📋 Policy Analytics Dashboard")
    
    # Sidebar filters
    st.sidebar.header("Policy Filters")
    
    carrier_name = st.sidebar.text_input(
        "Carrier Name",
        value="Acme Insurance Co",
        help="Filter by carrier name"
    )
    
    snapshot_date = st.sidebar.text_input(
        "Snapshot Date",
        value="2024-10-31",
        help="Policy snapshot date (YYYY-MM-DD format)"
    )
    
    state_filter = st.sidebar.text_input(
        "State",
        value="",
        help="Filter by state (optional)"
    )
    
    # Fetch data button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    try:
        # Fetch policy insights
        with st.spinner("Loading policy data..."):
            insights = api_client.get_policy_insights(
                carrier_name=carrier_name,
                snapshot_date=snapshot_date
            )
        
        if not insights:
            st.warning("No policy data available for the selected filters.")
            return
        
        metrics = insights.get("metrics", {})
        state_distribution = insights.get("state_distribution", {})
        premium_by_state = insights.get("premium_by_state", {})
        waiver_breakdown = insights.get("waiver_breakdown", {})
        status_distribution = insights.get("status_distribution", {})
        
        # KPI Cards - Row 1
        st.header("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_policies = metrics.get("total_policies", 0)
            st.metric(
                "Total Policies",
                format_number(total_policies),
                help="Total number of policies"
            )
        
        with col2:
            active_policies = metrics.get("active_policies", 0)
            st.metric(
                "Active Policies",
                format_number(active_policies),
                delta=format_percentage((active_policies / total_policies * 100) if total_policies > 0 else 0),
                help="Currently active policies"
            )
        
        with col3:
            lapse_rate = metrics.get("lapse_rate", 0)
            st.metric(
                "Lapse Rate",
                format_percentage(lapse_rate),
                delta=f"{total_policies - active_policies} lapsed",
                delta_color="inverse",
                help="Percentage of lapsed policies"
            )
        
        with col4:
            avg_premium = metrics.get("avg_premium", 0)
            st.metric(
                "Avg Premium",
                format_currency(avg_premium),
                help="Average annualized premium"
            )
        
        # KPI Cards - Row 2
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            total_revenue = metrics.get("total_premium_revenue", 0)
            st.metric(
                "Total Premium Revenue",
                format_currency(total_revenue, decimals=0),
                help="Total annualized premium revenue"
            )
        
        with col6:
            avg_age = metrics.get("avg_insured_age", 0)
            # Convert to float if it's a string
            try:
                avg_age_val = float(avg_age) if avg_age else 0
                age_display = f"{avg_age_val:.1f} years" if avg_age_val else "N/A"
            except (ValueError, TypeError):
                age_display = "N/A"
            st.metric(
                "Avg Insured Age",
                age_display,
                help="Average age of insured lives"
            )
        
        with col7:
            in_waiver = metrics.get("in_waiver_policies", 0)
            st.metric(
                "In Waiver",
                format_number(in_waiver),
                delta=format_percentage((in_waiver / total_policies * 100) if total_policies > 0 else 0),
                help="Policies in waiver status"
            )
        
        with col8:
            in_forfeiture = metrics.get("in_forfeiture_policies", 0)
            st.metric(
                "In Forfeiture",
                format_number(in_forfeiture),
                delta=format_percentage((in_forfeiture / total_policies * 100) if total_policies > 0 else 0),
                help="Policies in nonforfeiture status"
            )
        
        # KPI Cards - Row 3 (Claims related)
        col9, col10, col11, col12 = st.columns(4)
        
        with col9:
            policies_with_claims = metrics.get("policies_with_claims", 0)
            st.metric(
                "Policies with Claims",
                format_number(policies_with_claims),
                delta=format_percentage((policies_with_claims / total_policies * 100) if total_policies > 0 else 0),
                help="Policies that have active claims"
            )
        
        with col10:
            avg_claims = metrics.get("avg_claims_per_policy", 0)
            # Convert to float if it's a string
            try:
                avg_claims_val = float(avg_claims) if avg_claims else 0
                claims_display = f"{avg_claims_val:.2f}"
            except (ValueError, TypeError):
                claims_display = "0.00"
            st.metric(
                "Avg Claims/Policy",
                claims_display,
                help="Average claims per policy"
            )
        
        with col11:
            st.metric(
                "Active Status",
                format_number(status_distribution.get("Active", 0)),
                help="Policies in active status"
            )
        
        with col12:
            st.metric(
                "Lapsed Status",
                format_number(status_distribution.get("Lapsed", 0)),
                help="Policies in lapsed status"
            )
        
        # Charts Row 1
        st.header("Policy Distribution")
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Policy status distribution
            if status_distribution:
                st.subheader("Status Distribution")
                fig_status = go.Figure(data=[go.Pie(
                    labels=list(status_distribution.keys()),
                    values=list(status_distribution.values()),
                    hole=0.4,
                    marker=dict(colors=['#00CC96', '#EF553B'])
                )])
                fig_status.update_layout(height=350)
                st.plotly_chart(fig_status)
            else:
                st.info("No status distribution data available")
        
        with col_right:
            # Waiver breakdown
            if waiver_breakdown:
                st.subheader("Waiver Status")
                fig_waiver = go.Figure(data=[go.Bar(
                    x=list(waiver_breakdown.keys()),
                    y=list(waiver_breakdown.values()),
                    marker_color=['#FFA15A', '#636EFA'],
                    text=list(waiver_breakdown.values()),
                    textposition='auto'
                )])
                fig_waiver.update_layout(
                    height=350,
                    xaxis_title="Waiver Status",
                    yaxis_title="Number of Policies"
                )
                st.plotly_chart(fig_waiver)
            else:
                st.info("No waiver data available")
        
        # Charts Row 2
        st.header("Geographic Analysis")
        col_left2, col_right2 = st.columns(2)
        
        with col_left2:
            # State distribution (top 10)
            if state_distribution:
                st.subheader("Policies by State (Top 10)")
                # Sort and get top 10
                sorted_states = dict(sorted(
                    state_distribution.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10])
                
                fig_states = go.Figure(data=[go.Bar(
                    x=list(sorted_states.values()),
                    y=list(sorted_states.keys()),
                    orientation='h',
                    marker_color='#636EFA'
                )])
                fig_states.update_layout(
                    height=400,
                    xaxis_title="Number of Policies",
                    yaxis_title="State",
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig_states)
            else:
                st.info("No state distribution data available")
        
        with col_right2:
            # Premium revenue by state (top 10)
            if premium_by_state:
                st.subheader("Premium Revenue by State (Top 10)")
                # Sort and get top 10
                sorted_premium = dict(sorted(
                    premium_by_state.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10])
                
                fig_premium = go.Figure(data=[go.Bar(
                    x=list(sorted_premium.values()),
                    y=list(sorted_premium.keys()),
                    orientation='h',
                    marker_color='#00CC96',
                    text=[format_currency(v, decimals=0) for v in sorted_premium.values()],
                    textposition='auto'
                )])
                fig_premium.update_layout(
                    height=400,
                    xaxis_title="Premium Revenue ($)",
                    yaxis_title="State",
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig_premium)
            else:
                st.info("No premium by state data available")
        
        # Recent Policies Table
        st.header("Recent Policies")
        
        # Fetch policies list
        policies_list = api_client.get_policies(
            carrier_name=carrier_name,
            snapshot_date=snapshot_date,
            state=state_filter if state_filter else None,
            limit=50
        )
        
        if policies_list:
            # Convert to DataFrame
            df = pd.DataFrame(policies_list)
            
            # Select and format columns
            display_columns = [
                'POLICY_ID', 'CARRIER_NAME', 'INSURED_STATE',
                'ANNUALIZED_PREMIUM', 'RATED_AGE',
                'IN_WAIVER_FLG', 'IN_NONFORFEITURE_FLG',
                'TOTAL_ACTIVE_CLAIMS'
            ]
            
            # Filter existing columns (handle case sensitivity)
            actual_columns = []
            for col in display_columns:
                if col in df.columns:
                    actual_columns.append(col)
                elif col.lower() in df.columns:
                    actual_columns.append(col.lower())
            
            if actual_columns:
                df_display = df[actual_columns].copy()
                
                # Rename columns
                column_rename = {
                    'POLICY_ID': 'Policy ID',
                    'policy_id': 'Policy ID',
                    'CARRIER_NAME': 'Carrier',
                    'carrier_name': 'Carrier',
                    'INSURED_STATE': 'State',
                    'insured_state': 'State',
                    'ANNUALIZED_PREMIUM': 'Annual Premium',
                    'annualized_premium': 'Annual Premium',
                    'RATED_AGE': 'Age',
                    'rated_age': 'Age',
                    'IN_WAIVER_FLG': 'Waiver',
                    'in_waiver_flg': 'Waiver',
                    'IN_NONFORFEITURE_FLG': 'Forfeiture',
                    'in_nonforfeiture_flg': 'Forfeiture',
                    'TOTAL_ACTIVE_CLAIMS': 'Active Claims',
                    'total_active_claims': 'Active Claims'
                }
                df_display.rename(columns=column_rename, inplace=True)
                
                # Format premium column if exists
                if 'Annual Premium' in df_display.columns:
                    df_display['Annual Premium'] = df_display['Annual Premium'].apply(
                        lambda x: format_currency(x) if pd.notna(x) else 'N/A'
                    )
                
                # Display table
                st.dataframe(
                    df_display,
                    height=400
                )
                
                # Download button
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label="📥 Download Policy Data (CSV)",
                    data=csv,
                    file_name=f"policy_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No displayable columns found in the policy data.")
        else:
            st.info("No policies found matching the selected filters.")
    
    except Exception as e:
        st.error(f"Error loading policy data: {str(e)}")
        st.exception(e)

