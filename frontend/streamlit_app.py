"""Main Streamlit application for LTC Insurance Data Service."""

import sys
from pathlib import Path
from typing import Optional
from datetime import date, timedelta

# Add frontend directory to Python path
frontend_dir = Path(__file__).parent
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))

import streamlit as st

from components.claims_dashboard import render_claims_dashboard
from components.policy_analytics import render_policy_analytics
from services.api_client import APIClient, get_api_client

# Page configuration
st.set_page_config(
    page_title="LTC Insurance Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def check_api_connection(api_client: APIClient) -> bool:
    """
    Check API connection status.

    Args:
        api_client: API client instance

    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        health = api_client.health_check()
        return health.status == "healthy"
    except Exception:
        return False


def render_sidebar(api_client: APIClient) -> tuple[Optional[date], Optional[date], str]:
    """
    Render sidebar with filters and navigation.

    Args:
        api_client: API client instance

    Returns:
        Tuple of (start_date, end_date, page_selection)
    """
    with st.sidebar:
        st.title("🏥 LTC Insurance Analytics")
        st.markdown("---")

        # API Connection Status
        st.subheader("🔌 Connection Status")
        if check_api_connection(api_client):
            st.success("✅ Connected to API")
        else:
            st.error("❌ API Connection Failed")
            st.warning("Please check that the backend API is running at http://localhost:8000")

        st.markdown("---")

        # Navigation
        st.subheader("📍 Navigation")
        page = st.radio(
            "Select Dashboard",
            ["Home", "Claims Analytics", "Policy Analytics", "About"],
        )

        st.markdown("---")

        # Date Range Filter
        st.subheader("📅 Date Range Filter")

        use_date_filter = st.checkbox("Apply date filter", value=False)

        if use_date_filter:
            default_end = date.today()
            default_start = default_end - timedelta(days=365)

            start_date = st.date_input(
                "Start Date",
                value=default_start,
                max_value=default_end,
            )

            end_date = st.date_input(
                "End Date",
                value=default_end,
                min_value=start_date,
                max_value=default_end,
            )
        else:
            start_date = None
            end_date = None

        st.markdown("---")

        # Additional Info
        st.subheader("ℹ️ About")
        st.info(
            """
            **LTC Insurance Data Service**
            
            A comprehensive analytics platform for long-term care insurance data.
            
            - Real-time analytics
            - Interactive visualizations
            - Powered by Snowflake
            """
        )

        st.markdown("---")
        st.caption("Version 1.0.0 | © 2024")

    return start_date, end_date, page


def render_home_page(api_client: APIClient) -> None:
    """Render home page with overview."""
    st.title("🏥 Long-Term Care Insurance Analytics Platform")

    st.markdown(
        """
        ## Welcome to the LTC Insurance Data Service
        
        This platform provides comprehensive analytics and insights for long-term care insurance operations.
        
        ### 📊 Features
        
        - **Claims Analytics**: Track claim submissions, approvals, denials, and processing times
        - **Policy Metrics**: Monitor policy distribution, lapse rates, and premium revenue
        - **Custom Filters**: Filter data by date range, policy type, and more
        - **Real-time Data**: Direct integration with Snowflake data warehouse
        - **Interactive Visualizations**: Explore data with dynamic charts and graphs
        
        ### 🚀 Getting Started
        
        1. Select a dashboard from the sidebar navigation
        2. Apply optional date range filters
        3. Explore the interactive visualizations and metrics
        
        ### 📈 Available Dashboards
        
        **Claims Analytics Dashboard**
        - Total claims and approval rates
        - Processing time analysis
        - Claims distribution by status
        - Recent claims activity
        
        **Policy Analytics Dashboard**
        - Active policy metrics
        - Lapse rate analysis
        - Premium and benefit analysis
        - Policy type distribution
        
        ---
        
        Use the sidebar to navigate between dashboards and apply filters.
        """
    )

    # Show quick stats if API is available
    st.subheader("📊 Quick Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            """
            **Claims Dashboard**
            
            View comprehensive claims analytics including approval rates,
            processing times, and financial summaries.
            """
        )

    with col2:
        st.info(
            """
            **Policy Dashboard**
            
            Analyze policy portfolio health, retention metrics,
            and premium revenue trends.
            """
        )


def render_about_page() -> None:
    """Render about page."""
    st.title("ℹ️ About LTC Insurance Data Service")

    st.markdown(
        """
        ## Overview
        
        The LTC Insurance Data Service is a production-ready data-as-a-service platform
        designed specifically for long-term care insurance analytics.
        
        ### 🏗️ Architecture
        
        **Backend**
        - FastAPI REST API with async support
        - Snowpark for Snowflake integration
        - Repository pattern for data access
        - Caching layer for performance
        - Structured logging with JSON output
        
        **Frontend**
        - Streamlit for interactive dashboards
        - Plotly for visualizations
        - Type-safe API client with retry logic
        - Responsive design
        
        **Database**
        - Snowflake data warehouse
        - Optimized query performance
        - Scalable architecture
        
        ### 🔧 Technology Stack
        
        **Backend Technologies**
        - FastAPI 0.104+
        - Snowflake Snowpark
        - Pydantic for validation
        - Structlog for logging
        - Redis for caching (optional)
        
        **Frontend Technologies**
        - Streamlit 1.28+
        - Plotly for charts
        - Pandas for data manipulation
        - HTTPX for async requests
        
        ### 📝 API Documentation
        
        The backend API provides OpenAPI documentation at:
        - Swagger UI: http://localhost:8000/api/v1/docs
        - ReDoc: http://localhost:8000/api/v1/redoc
        
        ### 🎯 Key Features
        
        - **Advanced Python Patterns**: Type hints, async/await, dependency injection
        - **Production-Ready**: Error handling, logging, monitoring
        - **Performance**: Caching, connection pooling, query optimization
        - **Security**: Input validation, parameterized queries
        - **Scalability**: Stateless design, horizontal scaling support
        
        ### 📧 Contact
        
        For questions or support, please contact your system administrator.
        
        ---
        
        **Version**: 1.0.0  
        **Last Updated**: 2024
        """
    )


def main() -> None:
    """Main application entry point."""
    # Get API client
    api_client = get_api_client()

    # Render sidebar and get filters
    start_date, end_date, page = render_sidebar(api_client)

    # Render selected page
    if page == "Home":
        render_home_page(api_client)
    elif page == "Claims Analytics":
        render_claims_dashboard(api_client, start_date, end_date)
    elif page == "Policy Analytics":
        render_policy_analytics(api_client, start_date, end_date)
    elif page == "About":
        render_about_page()


if __name__ == "__main__":
    main()

