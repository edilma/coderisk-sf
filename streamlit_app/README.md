# 🏠 Property Risk Assessment Dashboard

An interactive Streamlit application for analyzing structural risk across multiple cities using the Structural Risk Index (SRI) methodology.

## 🚀 Features

### Interactive Filters
- **City Selection**: View all cities or focus on specific jurisdiction
- **Risk Score Range**: Adjust SRI score thresholds dynamically
- **Risk Categories**: Filter by High/Medium/Low risk levels
- **Violation Types**: Include/exclude specific violation categories
- **Results Limit**: Control number of properties displayed

### Real-Time Visualizations
- **Risk Score Distribution**: Histogram showing property risk spread
- **City Risk Comparison**: Bar chart or pie chart of risk levels
- **Interactive Property Table**: Sortable, color-coded results
- **Key Metrics Dashboard**: Summary statistics that update instantly

### Export Capabilities
- **CSV Downloads**: Filtered property results
- **Summary Reports**: Statistical summaries
- **Custom File Names**: Based on selected filters

## 🎯 Perfect for Demonstrations

This app is designed for:
- **YouTube video demos** - Smooth interactions for screen recording
- **Stakeholder presentations** - Professional, clean interface
- **Live analysis sessions** - Real-time filter adjustments
- **Educational purposes** - Clear visualization of risk methodology

## 🛠️ Usage

### Running the App
```bash
# Make sure you're in the project root directory with virtual environment activated
cd streamlit_app
streamlit run app.py
```

### Demo Script Ideas
1. **City Comparison**: "Let's see how Pompano Beach compares to other cities..."
2. **Risk Filtering**: "What happens when we only look at high-risk properties..."
3. **Violation Analysis**: "Here are all properties with unsafe structures..."
4. **Export Functionality**: "And we can download these results for further analysis..."

## 📊 Data Requirements

The app automatically loads data from:
- `../clean_data/structural_risk_index_results.csv`

This file should contain columns:
- `address`: Property address
- `city`: City name
- `total_sri_score`: Calculated SRI score
- `total_violations`: Number of violations
- `unsafe_structure_violations`: Count of unsafe structure violations
- `work_without_permit_violations`: Count of permit violations
- `inspection_40_50_violations`: Count of inspection violations
- `nuisance_maintenance_violations`: Count of maintenance violations
- `other_violations`: Count of other violations

## 🎨 Customization

The app includes:
- **Professional color scheme** matching your analysis theme
- **Responsive design** that works on different screen sizes
- **Custom CSS styling** for polished appearance
- **Risk-based color coding** (Red/Orange/Green)

## 📹 YouTube Demo Tips

For best screen recording results:
- Use wide layout mode (default)
- Interact with filters slowly to show real-time updates
- Click through different cities to show data variety
- Demonstrate export functionality
- Zoom browser to 100% for crisp recording

## 🔧 Technical Details

- Built with **Streamlit** for rapid development
- Uses **Plotly** for interactive charts
- Implements **caching** for performance
- **Responsive design** for various screen sizes
- **Error handling** for missing data

Perfect for showcasing the practical value of your SRI analysis system!