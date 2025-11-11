import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pathlib
import sys

# Add parent directory to path to import our modules
parent_dir = pathlib.Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Page configuration
st.set_page_config(
    page_title="Property Risk Intelligence Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-high { color: #d32f2f; font-weight: bold; }
    .risk-medium { color: #ff9800; font-weight: bold; }
    .risk-low { color: #4caf50; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sri_data():
    """Load the SRI results data"""
    try:
        # Get the correct path to the clean_data directory
        current_dir = pathlib.Path(__file__).parent.resolve()
        project_root = current_dir.parent
        data_path = project_root / "clean_data" / "structural_risk_index_results.csv"
        
        # Try alternative paths if main path doesn't exist
        if not data_path.exists():
            alt_path = pathlib.Path("../clean_data/structural_risk_index_results.csv")
            if alt_path.exists():
                data_path = alt_path
        
        if not data_path.exists():
            import os
            cwd = pathlib.Path(os.getcwd())
            alt_path2 = cwd.parent / "clean_data" / "structural_risk_index_results.csv"
            if alt_path2.exists():
                data_path = alt_path2
        
        if data_path.exists():
            df = pd.read_csv(data_path)
            return df
        else:
            st.error(f"SRI data file not found. Please ensure the SRI analysis has been run.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def get_risk_category(score):
    """Categorize risk score"""
    if score >= 8:
        return "High"
    elif score >= 4:
        return "Medium"
    else:
        return "Low"

def get_risk_color(category):
    """Get color for risk category"""
    colors = {"High": "#d32f2f", "Medium": "#ff9800", "Low": "#4caf50"}
    return colors.get(category, "#gray")

def main():
    # App header
    st.markdown('<h1 class="main-header">Property Risk Intelligence Platform</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #666; margin-top: -1rem;">using Structural Risk Index (SRI)</h3>', unsafe_allow_html=True)
    
    # Load data
    df = load_sri_data()
    
    if df.empty:
        st.error("No data available. Please ensure the SRI analysis has been run.")
        st.stop()
    
    # Add risk categories
    df['risk_category'] = df['total_sri_score'].apply(get_risk_category)
    df['risk_color'] = df['risk_category'].apply(get_risk_color)
    
    # Normalize scores to 0-100 scale for intuitive display
    max_score = df['total_sri_score'].max()
    df['sri_normalized'] = (df['total_sri_score'] / max_score * 100).round(1)
    
    # Sidebar filters
    st.sidebar.header("Filter Options")
    
    # City filter
    cities = ['All Cities'] + sorted(df['city'].unique().tolist())
    selected_city = st.sidebar.selectbox("Select City", cities)
    
    # SRI score range filter
    min_score, max_score = int(df['total_sri_score'].min()), int(df['total_sri_score'].max())
    score_range = st.sidebar.slider(
        "SRI Score Range", 
        min_value=min_score, 
        max_value=max_score, 
        value=(min_score, max_score),
        help=f"Filter properties by SRI score (1-{max_score})"
    )
    
    # Risk category filter
    risk_categories = st.sidebar.multiselect(
        "Risk Categories",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"],
        help="Select which risk levels to include"
    )
    
    # Violation type filters
    st.sidebar.subheader("Include Violation Types")
    st.sidebar.caption("Show properties that have at least one selected violation type")
    include_unsafe = st.sidebar.checkbox("Unsafe Structure", value=True)
    include_permit = st.sidebar.checkbox("Work Without Permit", value=True)
    include_inspection = st.sidebar.checkbox("40/50 Year Inspection", value=True)
    include_maintenance = st.sidebar.checkbox("Nuisance/Maintenance", value=True)
    include_other = st.sidebar.checkbox("Other Violations", value=True)
    
    # Debug: Show violation counts by city
    if st.sidebar.checkbox("Show violation distribution debug", value=False):
        st.sidebar.write("Violation counts by city:")
        for city in df['city'].unique():
            city_data = df[df['city'] == city]
            st.sidebar.write(f"{city}:")
            st.sidebar.write(f"  - Total properties: {len(city_data)}")
            st.sidebar.write(f"  - With 40/50 inspections: {len(city_data[city_data['inspection_40_50_violations'] > 0])}")
            st.sidebar.write(f"  - With unsafe structure: {len(city_data[city_data['unsafe_structure_violations'] > 0])}")
            st.sidebar.write(f"  - With permit issues: {len(city_data[city_data['work_without_permit_violations'] > 0])}")
            st.sidebar.write(f"  - With maintenance: {len(city_data[city_data['nuisance_maintenance_violations'] > 0])}")
    
    # Results limit
    results_limit = st.sidebar.slider("Maximum Results to Show", 10, 500, 100)
    
    # Apply filters
    filtered_df = df.copy()
    
    # City filter
    if selected_city != 'All Cities':
        filtered_df = filtered_df[filtered_df['city'] == selected_city]
    
    # Score range filter
    filtered_df = filtered_df[
        (filtered_df['total_sri_score'] >= score_range[0]) & 
        (filtered_df['total_sri_score'] <= score_range[1])
    ]
    
    # Risk category filter
    filtered_df = filtered_df[filtered_df['risk_category'].isin(risk_categories)]
    
    # Apply violation type filters - NEW LOGIC: Only include if at least one selected violation type is present
    violation_conditions = []
    if include_unsafe:
        violation_conditions.append(filtered_df['unsafe_structure_violations'] > 0)
    if include_permit:
        violation_conditions.append(filtered_df['work_without_permit_violations'] > 0)
    if include_inspection:
        violation_conditions.append(filtered_df['inspection_40_50_violations'] > 0)
    if include_maintenance:
        violation_conditions.append(filtered_df['nuisance_maintenance_violations'] > 0)
    if include_other:
        violation_conditions.append(filtered_df['other_violations'] > 0)
    
    # If at least one violation type is selected, filter to show only properties with those violations
    if violation_conditions:
        # Combine conditions with OR - property must have at least one of the selected violation types
        combined_condition = violation_conditions[0]
        for condition in violation_conditions[1:]:
            combined_condition = combined_condition | condition
        filtered_df = filtered_df[combined_condition]
    # If no violation types are selected, show no properties
    elif not any([include_unsafe, include_permit, include_inspection, include_maintenance, include_other]):
        filtered_df = filtered_df.iloc[0:0]  # Empty dataframe
    
    # Store full filtered results for metrics (before limiting)
    full_filtered_df = filtered_df.copy()
    
    # Limit results for display
    display_df = filtered_df.head(results_limit)
    
    # Main dashboard
    if full_filtered_df.empty:
        st.warning("No properties match the selected filters. Please adjust your criteria.")
        return
    
    # Key metrics row (based on FULL filtered data, not limited)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Properties", f"{len(full_filtered_df):,}")
    
    with col2:
        high_risk_count = len(full_filtered_df[full_filtered_df['risk_category'] == 'High'])
        high_risk_pct = (high_risk_count / len(full_filtered_df) * 100) if len(full_filtered_df) > 0 else 0
        st.metric("High Risk Properties", f"{high_risk_count}", f"{high_risk_pct:.1f}%")
    
    with col3:
        avg_score = full_filtered_df['total_sri_score'].mean()
        st.metric("Average SRI Score", f"{avg_score:.1f}")
    
    with col4:
        max_score_property = full_filtered_df['total_sri_score'].max()
        st.metric("Highest Risk Score", f"{max_score_property}")
    
    # Charts row (using full filtered data)
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk distribution chart
        fig_dist = px.histogram(
            full_filtered_df, 
            x='total_sri_score',
            nbins=20,
            title="Risk Score Distribution",
            labels={'total_sri_score': 'SRI Score', 'count': 'Number of Properties'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Risk categories by city
        if selected_city == 'All Cities':
            city_risk = full_filtered_df.groupby(['city', 'risk_category']).size().reset_index(name='count')
            fig_city = px.bar(
                city_risk,
                x='city',
                y='count',
                color='risk_category',
                title="Risk Distribution by City",
                color_discrete_map={"High": "#d32f2f", "Medium": "#ff9800", "Low": "#4caf50"}
            )
        else:
            risk_counts = full_filtered_df['risk_category'].value_counts()
            fig_city = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title=f"Risk Distribution - {selected_city}",
                color_discrete_map={"High": "#d32f2f", "Medium": "#ff9800", "Low": "#4caf50"}
            )
        
        fig_city.update_layout(height=400)
        st.plotly_chart(fig_city, use_container_width=True)
    
    # Properties table
    st.subheader("Filtered Properties")
    if len(full_filtered_df) > results_limit:
        st.info(f"Showing top {results_limit} of {len(full_filtered_df)} matching properties. Adjust the 'Maximum Results' slider to see more.")
    
    # Prepare display dataframe (using limited results)
    table_df = display_df[['address', 'city', 'total_sri_score', 'sri_normalized', 'risk_category', 
                          'total_violations', 'unsafe_structure_violations', 'work_without_permit_violations',
                          'inspection_40_50_violations', 'nuisance_maintenance_violations', 'other_violations']].copy()
    
    table_df = table_df.rename(columns={
        'address': 'Address',
        'city': 'City',
        'total_sri_score': 'SRI Score',
        'sri_normalized': 'SRI (0-100)',
        'risk_category': 'Risk Level',
        'total_violations': 'Total Violations',
        'unsafe_structure_violations': 'Unsafe Structure',
        'work_without_permit_violations': 'No Permit',
        'inspection_40_50_violations': '40/50 Yr Inspect',
        'nuisance_maintenance_violations': 'Maintenance',
        'other_violations': 'Other'
    })
    
    # Color-code the risk levels
    def highlight_risk(row):
        if row['Risk Level'] == 'High':
            return ['background-color: #ffebee'] * len(row)
        elif row['Risk Level'] == 'Medium':
            return ['background-color: #fff3e0'] * len(row)
        else:
            return ['background-color: #e8f5e8'] * len(row)
    
    styled_df = table_df.style.apply(highlight_risk, axis=1)
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # Download section
    st.subheader("Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        # Prepare full filtered data for download
        download_df = full_filtered_df[['address', 'city', 'total_sri_score', 'sri_normalized', 'risk_category', 
                                       'total_violations', 'unsafe_structure_violations', 'work_without_permit_violations',
                                       'inspection_40_50_violations', 'nuisance_maintenance_violations', 'other_violations']].copy()
        download_df = download_df.rename(columns={
            'address': 'Address',
            'city': 'City',
            'total_sri_score': 'SRI Score',
            'sri_normalized': 'SRI (0-100)',
            'risk_category': 'Risk Level',
            'total_violations': 'Total Violations',
            'unsafe_structure_violations': 'Unsafe Structure',
            'work_without_permit_violations': 'No Permit',
            'inspection_40_50_violations': '40/50 Yr Inspect',
            'nuisance_maintenance_violations': 'Maintenance',
            'other_violations': 'Other'
        })
        
        csv = download_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Results (CSV)",
            data=csv,
            file_name=f"property_risk_results_{selected_city.replace(' ', '_')}.csv",
            mime='text/csv'
        )
    
    with col2:
        # Summary statistics (using full filtered data)
        summary_stats = {
            'Total Properties': len(full_filtered_df),
            'High Risk Properties': len(full_filtered_df[full_filtered_df['risk_category'] == 'High']),
            'Medium Risk Properties': len(full_filtered_df[full_filtered_df['risk_category'] == 'Medium']),
            'Low Risk Properties': len(full_filtered_df[full_filtered_df['risk_category'] == 'Low']),
            'Average SRI Score': f"{full_filtered_df['total_sri_score'].mean():.2f}",
            'Maximum SRI Score': full_filtered_df['total_sri_score'].max(),
            'Selected City': selected_city,
            'Score Range': f"{score_range[0]}-{score_range[1]}"
        }
        
        summary_text = "\n".join([f"{k}: {v}" for k, v in summary_stats.items()])
        st.download_button(
            label="Download Summary Stats",
            data=summary_text,
            file_name=f"risk_summary_{selected_city.replace(' ', '_')}.txt",
            mime='text/plain'
        )
    
    # Footer
    st.markdown("---")
    st.markdown("**Property Risk Intelligence Platform** - Built with Streamlit | Powered by Structural Risk Index (SRI)")

if __name__ == "__main__":
    main()