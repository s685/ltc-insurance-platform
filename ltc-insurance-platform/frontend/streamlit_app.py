"""Main Streamlit application for LTC Insurance Data Service Platform."""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.api_client import APIClient
from components.claims_dashboard import render_claims_dashboard
from components.policy_analytics import render_policy_dashboard


# Page configuration
st.set_page_config(
    page_title="LTC Insurance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    h1 {
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""
    
    # Initialize API client
    api_base_url = st.secrets.get("API_BASE_URL", "http://localhost:8000")
    api_client = APIClient(base_url=api_base_url)
    
    # Sidebar navigation
    st.sidebar.title("🏥 LTC Insurance Platform")
    st.sidebar.markdown("---")
    
    # Check API health
    health_status = api_client.health_check()
    
    if health_status.get("status") == "healthy":
        st.sidebar.success("✅ API Connected")
    elif health_status.get("status") == "degraded":
        st.sidebar.warning("⚠️ API Degraded (DB Issue)")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.error("Cannot connect to backend API. Please ensure the backend is running.")
        st.info(f"Expected API URL: {api_base_url}")
        st.stop()
    
    # Navigation menu
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "Select Dashboard",
        ["🏠 Home", "📊 Claims Analytics", "📋 Policy Analytics", "ℹ️ About"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Info")
    st.sidebar.info(f"""
    **Version:** {health_status.get('version', 'Unknown')}  
    **Database:** {'✓' if health_status.get('database_connected') else '✗'}  
    **Cache:** {'✓' if health_status.get('cache_enabled') else '✗'}
    """)
    
    # Render selected page
    if page == "🏠 Home":
        render_home_page(api_client)
    elif page == "📊 Claims Analytics":
        render_claims_dashboard(api_client)
    elif page == "📋 Policy Analytics":
        render_policy_dashboard(api_client)
    elif page == "ℹ️ About":
        render_about_page()


def render_home_page(api_client: APIClient):
    """Render home/landing page."""
    st.title("🏥 LTC Insurance Data Service Platform")
    st.markdown("### Welcome to the Analytics Dashboard")
    
    st.markdown("""
    This platform provides comprehensive analytics for Long-Term Care insurance data,
    including claims processing insights and policy analytics.
    """)
    
    # Quick stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Claims Analytics")
        st.markdown("""
        - **Approval Rates:** Track claim approval and denial rates
        - **Processing Times:** Monitor turnaround times (TAT)
        - **Retro Analysis:** Analyze retroactive claims
        - **Category Breakdown:** Facility, Home Health, and Other
        - **Decision Types:** Initial, Ongoing, Restoration
        
        Navigate to **Claims Analytics** to explore detailed insights.
        """)
    
    with col2:
        st.markdown("#### 📋 Policy Analytics")
        st.markdown("""
        - **Policy Metrics:** Active policies, lapse rates
        - **Premium Analysis:** Revenue and average premiums
        - **Waiver Status:** Track waiver and nonforfeiture
        - **Geographic Distribution:** Policies and revenue by state
        - **Claims Correlation:** Policies with active claims
        
        Navigate to **Policy Analytics** to view comprehensive metrics.
        """)
    
    st.markdown("---")
    
    # Combined dashboard preview
    st.header("📈 Dashboard Overview")
    
    try:
        with st.spinner("Loading dashboard preview..."):
            dashboard_data = api_client.get_combined_dashboard(
                carrier_name="Acme Insurance Co",
                snapshot_date="2024-10-31"
            )
        
        if dashboard_data:
            col_a, col_b, col_c, col_d = st.columns(4)
            
            policy_metrics = dashboard_data.get("policy_metrics", {})
            claims_summary = dashboard_data.get("claims_summary", {})
            
            with col_a:
                st.metric(
                    "Total Policies",
                    f"{policy_metrics.get('total_policies', 0):,}"
                )
            
            with col_b:
                st.metric(
                    "Active Policies",
                    f"{policy_metrics.get('active_policies', 0):,}"
                )
            
            with col_c:
                st.metric(
                    "Total Claims",
                    f"{claims_summary.get('total_claims', 0):,}"
                )
            
            with col_d:
                st.metric(
                    "Approval Rate",
                    f"{claims_summary.get('approval_rate', 0):.1f}%"
                )
            
            st.info("💡 Select a dashboard from the sidebar to see detailed analytics.")
        else:
            st.warning("Dashboard preview data not available.")
    
    except Exception as e:
        st.warning(f"Could not load dashboard preview: {str(e)}")
    
    # Getting started
    st.markdown("---")
    st.header("🚀 Getting Started")
    
    with st.expander("📖 How to Use This Platform"):
        st.markdown("""
        **1. Navigation:**
        - Use the sidebar to switch between Claims and Policy dashboards
        - Each dashboard has its own set of filters and visualizations
        
        **2. Filtering Data:**
        - Set filters in the sidebar (carrier, dates, decision types, etc.)
        - Click "Refresh Data" to apply filters
        - Filters are specific to each dashboard
        
        **3. Understanding Metrics:**
        - **Claims Dashboard:** Focus on claim processing and approval metrics
        - **Policy Dashboard:** Focus on policy status and premium analytics
        
        **4. Exporting Data:**
        - Each dashboard provides CSV download options
        - Download buttons are available below data tables
        
        **5. Data Refresh:**
        - Data is cached for 5 minutes for performance
        - Use the "Refresh Data" button to force a reload
        """)
    
    with st.expander("🔍 Key Features"):
        st.markdown("""
        **Claims Analytics:**
        - Real-time approval and denial tracking
        - Processing time (TAT) analysis
        - Retroactive claims identification
        - Multi-dimensional filtering (decision type, category, ongoing rate month)
        
        **Policy Analytics:**
        - Active vs lapsed policy tracking
        - Premium revenue analysis
        - Geographic distribution (by state)
        - Waiver and nonforfeiture status monitoring
        - Claims-to-policy correlation
        
        **Technical Features:**
        - FastAPI backend with Snowpark for Snowflake
        - Redis caching for improved performance
        - Type-safe API communication
        - Responsive visualizations with Plotly
        """)


def render_about_page():
    """Render about/information page."""
    st.title("ℹ️ About LTC Insurance Platform")
    
    st.markdown("""
    ## Overview
    
    The LTC Insurance Data Service Platform is a production-ready analytics solution
    designed for long-term care insurance data analysis.
    
    ### Architecture
    
    ```
    ┌─────────────────────────────────────────────────────────────┐
    │                     Streamlit Frontend                       │
    │  (Interactive Dashboards & Visualizations)                   │
    └────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    FastAPI Backend                           │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
    │  │   Services   │  │ Repositories │  │    Models    │      │
    │  │  (Business   │◄─┤   (Data      │◄─┤  (Schemas &  │      │
    │  │   Logic)     │  │   Access)    │  │   Domain)    │      │
    │  └──────────────┘  └──────────────┘  └──────────────┘      │
    │         │                  │                                 │
    │         └──────────────────┼─────────────────────────►      │
    │                            ▼                                 │
    │                    Snowpark Session                          │
    │                     (Connection Pool)                        │
    └────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────────┐
    │              Snowflake Data Warehouse                        │
    │  ┌──────────────┐  ┌──────────────┐                         │
    │  │   POLICIES   │  │    CLAIMS    │                         │
    │  └──────────────┘  └──────────────┘                         │
    └─────────────────────────────────────────────────────────────┘
    ```
    
    ### Technology Stack
    
    **Backend:**
    - FastAPI (REST API framework)
    - Snowpark (Snowflake Python SDK)
    - Redis (Caching layer)
    - Pydantic (Data validation)
    
    **Frontend:**
    - Streamlit (Web framework)
    - Plotly (Visualizations)
    - Pandas (Data manipulation)
    
    **Database:**
    - Snowflake (Cloud data warehouse)
    
    ### Key Features
    
    ✅ RESTful API with comprehensive endpoints  
    ✅ Snowpark integration with connection pooling  
    ✅ Repository pattern for clean data access  
    ✅ Service layer with business logic separation  
    ✅ Redis caching for improved performance  
    ✅ Type-safe API communication  
    ✅ Interactive dashboards with real-time data  
    ✅ Configurable filtering and analysis  
    
    ### Data Tables
    
    **POLICY_MONTHLY_SNAPSHOT_FACT:**
    - Policy details and status
    - Premium information
    - Waiver and nonforfeiture tracking
    - Claims correlation
    
    **CLAIMS_TPA_FEE_WORKSHEET_SNAPSHOT_FACT:**
    - Claims processing data
    - Decision tracking (Approved, Denied, In Assessment)
    - Turnaround time (TAT) metrics
    - Retroactive claims analysis
    - Category breakdown (Facility, Home Health, Other)
    
    ### Business Logic
    
    **Claims Filtering:**
    - Core filter: `(ONGOING_RATE_MONTH = 1 AND IS_INITIAL_DECISION_FLAG IN (0,1))
      OR (ONGOING_RATE_MONTH = 0 AND IS_INITIAL_DECISION_FLAG = 1)
      OR (ONGOING_RATE_MONTH = 2 AND IS_INITIAL_DECISION_FLAG IN (0,1))`
    - Configurable by carrier, date, decision type, and category
    
    **Ongoing Rate Months:**
    - 0: Initial Decision
    - 1: Ongoing
    - 2: Restoration of Benefits
    
    **Retro Claims:**
    - Identified by RETRO_MONTHS > 0
    - Analyzed by category (Facility, Home Health, Other)
    
    ### Version Information
    
    **Version:** 1.0.0  
    **Last Updated:** October 2024  
    **License:** Proprietary - Internal Use Only
    
    ### Support
    
    For questions or issues, please contact the development team.
    """)
    
    st.markdown("---")
    st.markdown("*Built with ❤️ using FastAPI, Snowpark, and Streamlit*")


if __name__ == "__main__":
    main()

