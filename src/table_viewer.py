import streamlit as st
import json
import pandas as pd
from pathlib import Path
from io import StringIO

def discover_cities_and_files():
    """Discover all cities and their JSON files from results_folder"""
    results_folder = Path("../results_folder")
    cities_data = {}
    
    if results_folder.exists():
        for city_folder in results_folder.iterdir():
            if city_folder.is_dir():
                raw_json_dir = city_folder / "raw_json"
                if raw_json_dir.exists():
                    json_files = list(raw_json_dir.glob("*.json"))
                    if json_files:
                        cities_data[city_folder.name] = {
                            'folder': city_folder,
                            'json_files': json_files
                        }
    
    return cities_data

def load_json_data(json_file_path):
    """Load and extract table chunks from JSON file"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    table_chunks = []
    if 'chunks' in data:
        for i, chunk in enumerate(data['chunks']):
            if chunk.get('type') == 'table' and 'markdown' in chunk:
                table_chunks.append({
                    'chunk_id': i,
                    'markdown': chunk['markdown'],
                    'chunk_info': {
                        'type': chunk.get('type'),
                        'bbox': chunk.get('bbox', {}),
                        'page': chunk.get('page', 'unknown')
                    }
                })
    return table_chunks

def main():
    st.set_page_config(page_title="Multi-City Table Viewer", layout="wide")
    
    st.title("🏙️ Multi-City PDF Table Structure Viewer")
    st.markdown("**Analyze raw HTML tables from LandingAI extraction across all cities**")
    
    # Discover available cities and files
    cities_data = discover_cities_and_files()
    
    if not cities_data:
        st.error("No cities with JSON files found in ../results_folder/")
        st.info("Make sure you're running this from the src/ directory and have extracted data")
        return
    
    # City and file selection
    st.sidebar.header("🏙️ City & File Selection")
    
    # City selector
    city_names = list(cities_data.keys())
    selected_city = st.sidebar.selectbox("Select City:", city_names)
    
    # File selector for selected city
    available_files = cities_data[selected_city]['json_files']
    file_options = [f.name for f in available_files]
    selected_file_idx = st.sidebar.selectbox(
        "Select JSON file:",
        range(len(file_options)),
        format_func=lambda x: file_options[x]
    )
    
    selected_file = available_files[selected_file_idx]
    
    # Display selected file info
    st.sidebar.info(f"**Selected:**\n\n🏙️ **City:** {selected_city.title()}\n\n📄 **File:** {selected_file.name}")
    
    # Load data
    with st.spinner(f"Loading table chunks from {selected_city}..."):
        table_chunks = load_json_data(selected_file)
    
    st.success(f"Found {len(table_chunks)} table chunks in {selected_city.title()}")
    
    # Sidebar for chunk selection
    st.sidebar.header("Table Chunk Selection")
    
    if table_chunks:
        chunk_options = [f"Chunk {chunk['chunk_id']+1} (Page {chunk['chunk_info'].get('page', '?')})" 
                        for chunk in table_chunks]
        
        selected_chunk_idx = st.sidebar.selectbox(
            "Select a table chunk to view:",
            range(len(chunk_options)),
            format_func=lambda x: chunk_options[x]
        )
        
        selected_chunk = table_chunks[selected_chunk_idx]
        
        # Display chunk info
        st.sidebar.json({
            "Chunk ID": selected_chunk['chunk_id'],
            "Type": selected_chunk['chunk_info']['type'],
            "Page": selected_chunk['chunk_info'].get('page', 'unknown'),
            "BBox": selected_chunk['chunk_info'].get('bbox', {})
        })
        
        # Main content - Side by side layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🎨 Rendered Table")
            
            # Try to render the HTML table
            try:
                if '<table' in selected_chunk['markdown'].lower():
                    # Display as HTML table
                    st.markdown(selected_chunk['markdown'], unsafe_allow_html=True)
                else:
                    st.info("No HTML table found in this chunk")
                    st.markdown(selected_chunk['markdown'])
                    
            except Exception as e:
                st.error(f"Error rendering table: {e}")
                st.text(selected_chunk['markdown'])
        
        with col2:
            st.subheader("🐼 Pandas Interpretation")
            
            try:
                if '<table' in selected_chunk['markdown'].lower():
                    # Try pandas parsing
                    tables = pd.read_html(StringIO(selected_chunk['markdown']))
                    if tables:
                        df = tables[0]
                        st.info(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                        st.dataframe(df, use_container_width=True)
                        
                        # Show column analysis
                        st.markdown("**Column Names:**")
                        cols_text = ""
                        for i, col in enumerate(df.columns):
                            cols_text += f"{i+1}. `{col}`\n"
                        st.markdown(cols_text)
                    else:
                        st.warning("No tables found in HTML")
                else:
                    st.info("Not an HTML table - showing as markdown")
                    st.markdown(selected_chunk['markdown'])
                    
            except Exception as e:
                st.error(f"Could not parse with pandas: {e}")
                st.code(selected_chunk['markdown'])
        
        # Raw HTML/Markdown at the bottom
        st.subheader("📄 Raw HTML/Markdown")
        with st.expander("Show Raw HTML/Markdown Content", expanded=False):
            st.code(selected_chunk['markdown'], language='html')
        
        # Summary section
        st.subheader(f"📋 All Table Chunks Summary - {selected_city.title()}")
        summary_data = []
        for chunk in table_chunks:
            try:
                if '<table' in chunk['markdown'].lower():
                    tables = pd.read_html(StringIO(chunk['markdown']))
                    if tables:
                        df = tables[0]
                        summary_data.append({
                            'Chunk': chunk['chunk_id'] + 1,
                            'Page': chunk['chunk_info'].get('page', '?'),
                            'Rows': df.shape[0],
                            'Columns': df.shape[1],
                            'First Column': str(df.columns[0]) if len(df.columns) > 0 else 'N/A',
                            'Has HTML': '<table' in chunk['markdown'].lower()
                        })
            except:
                summary_data.append({
                    'Chunk': chunk['chunk_id'] + 1,
                    'Page': chunk['chunk_info'].get('page', '?'),
                    'Rows': 'Error',
                    'Columns': 'Error',
                    'First Column': 'Error',
                    'Has HTML': '<table' in chunk['markdown'].lower()
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
            
            # Add city comparison section
            st.subheader("🏙️ Multi-City Overview")
            city_overview = []
            for city_name, city_info in cities_data.items():
                total_files = len(city_info['json_files'])
                city_overview.append({
                    'City': city_name.title(),
                    'JSON Files': total_files,
                    'Status': '✅ Available' if total_files > 0 else '❌ No Data'
                })
            
            overview_df = pd.DataFrame(city_overview)
            st.dataframe(overview_df, use_container_width=True)

if __name__ == "__main__":
    main()