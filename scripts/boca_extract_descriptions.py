#!/usr/bin/env python3
"""
Extract descriptions and their corresponding row data from Boca Raton and other cities' processed results.
"""

import pandas as pd
from pathlib import Path

def extract_descriptions_from_csv():
    """Extract descriptions from the combined CSV file or individual city files."""
    
    # Path to your combined results
    results_dir = Path("results_folder")
    combined_csv = results_dir / "ade_extracted_results.csv"
    combined_parquet = results_dir / "ade_extracted_results.parquet"
    
    # Try to load the data (prefer parquet for better type preservation)
    if combined_parquet.exists():
        print(f"Loading data from {combined_parquet}")
        df = pd.read_parquet(combined_parquet)
    elif combined_csv.exists():
        print(f"Loading data from {combined_csv}")
        df = pd.read_csv(combined_csv)
    else:
        # Try to load from individual city files
        print("No combined results file found. Looking for individual city files...")
        city_files = []
        for city_dir in results_dir.glob("*/tables/*.csv"):
            city_files.append(city_dir)
        
        if not city_files:
            print("No data files found. Run the extraction first.")
            return None
        
        print(f"Found {len(city_files)} city data files")
        frames = []
        for csv_file in city_files:
            city_name = csv_file.parent.parent.name
            try:
                city_df = pd.read_csv(csv_file)
                city_df['city'] = city_name
                frames.append(city_df)
                print(f"Loaded {len(city_df)} records from {city_name}")
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")
        
        if not frames:
            print("No valid data files found.")
            return None
        
        df = pd.concat(frames, ignore_index=True)
        print(f"Combined {len(df)} total records from all cities")
    
    print(f"Loaded {len(df)} total records")
    print(f"Columns available: {list(df.columns)}")
    
    # Check if Description column exists, or if descriptions are in other columns
    desc_cols = [col for col in df.columns if 'description' in col.lower()]
    if not desc_cols:
        # Look for descriptions in Main Address column (as seen in your data)
        if 'Main Address' in df.columns:
            desc_col = 'Main Address'
            print("Using 'Main Address' column to search for descriptions")
        else:
            print("No description column found in the data.")
            return None
    else:
        desc_col = desc_cols[0]  # Use the first description column found
        print(f"Using description column: '{desc_col}'")
    
    # Filter rows that have descriptions (look for "Description:" pattern)
    has_description = (
        ~df[desc_col].isna() & 
        df[desc_col].astype(str).str.contains('Description:', case=False, na=False)
    )
    df_with_desc = df[has_description].copy()
    
    print(f"Found {len(df_with_desc)} records with descriptions")
    
    if len(df_with_desc) == 0:
        print("No records with descriptions found.")
        return None
    
    # Select key columns along with description
    key_columns = [
        'Case Number', 'Case Type', 'Case Status', 'Main Address', 
        'Opened Date', 'Closed Date', 'city', 'source_file', desc_col
    ]
    
    # Only keep columns that exist in the dataframe
    available_columns = [col for col in key_columns if col in df_with_desc.columns]
    result_df = df_with_desc[available_columns].copy()
    
    # Sort by city and opened date
    if 'Opened Date' in result_df.columns:
        result_df = result_df.sort_values(['city', 'Opened Date'], na_position='last')
    else:
        result_df = result_df.sort_values('city')
    
    return result_df

def extract_boca_descriptions_only():
    """Extract descriptions specifically from Boca Raton records."""
    
    df = extract_descriptions_from_csv()
    if df is None:
        return None
    
    # Filter for Boca Raton records only
    boca_df = df[df['city'].str.contains('boca', case=False, na=False)].copy()
    
    if len(boca_df) == 0:
        print("No Boca Raton records with descriptions found.")
        return None
    
    print(f"Found {len(boca_df)} Boca Raton records with descriptions")
    return boca_df

def extract_descriptions_by_city():
    """Extract descriptions grouped by city."""
    
    df = extract_descriptions_from_csv()
    if df is None:
        return
    
    # Find the description column (could be 'Main Address' or actual 'Description')
    desc_cols = [col for col in df.columns if 'description' in col.lower()]
    if desc_cols:
        desc_col = desc_cols[0]
    elif 'Main Address' in df.columns:
        desc_col = 'Main Address'
    else:
        print("No description column found.")
        return
    
    print("\n" + "="*80)
    print("DESCRIPTIONS BY CITY")
    print("="*80)
    
    for city in sorted(df['city'].unique()):
        city_data = df[df['city'] == city]
        print(f"\n🏙️  {city.upper()} ({len(city_data)} records with descriptions)")
        print("-" * 60)
        
        for idx, row in city_data.head(10).iterrows():  # Show first 10 per city
            case_num = row.get('Case Number', 'N/A')
            address = row.get('Main Address', 'N/A')
            description = row[desc_col]
            
            print(f"Case: {case_num}")
            print(f"Address: {address}")
            print(f"Description: {description[:200]}{'...' if len(str(description)) > 200 else ''}")
            print()
        
        if len(city_data) > 10:
            print(f"... and {len(city_data) - 10} more records")
        print()

def save_boca_descriptions_to_file():
    """Save Boca descriptions to separate files for analysis."""
    
    df = extract_descriptions_from_csv()
    if df is None:
        return
    
    # Find the description column
    desc_cols = [col for col in df.columns if 'description' in col.lower()]
    if desc_cols:
        desc_col = desc_cols[0]
    elif 'Main Address' in df.columns:
        desc_col = 'Main Address'
    else:
        print("No description column found.")
        return
    
    # Create output directory
    output_dir = Path("results_folder/boca_descriptions_extracted")
    output_dir.mkdir(exist_ok=True)
    
    # Save all descriptions
    df.to_csv(output_dir / "all_descriptions.csv", index=False)
    df.to_parquet(output_dir / "all_descriptions.parquet", index=False)
    
    # Save Boca Raton specifically
    boca_df = extract_boca_descriptions_only()
    if boca_df is not None:
        boca_df.to_csv(output_dir / "boca_raton_descriptions.csv", index=False)
        boca_df.to_parquet(output_dir / "boca_raton_descriptions.parquet", index=False)
        
        # Save Boca descriptions as text for easy reading
        with open(output_dir / "boca_descriptions_only.txt", "w", encoding="utf-8") as f:
            for idx, row in boca_df.iterrows():
                case_num = row.get('Case Number', 'N/A')
                address = row.get('Main Address', 'N/A')
                description = row[desc_col]
                
                f.write(f"Case: {case_num} | Address: {address}\n")
                f.write(f"Description: {description}\n")
                f.write("-" * 80 + "\n\n")
    
    # Save by city
    for city in df['city'].unique():
        city_data = df[df['city'] == city]
        safe_city = city.replace(" ", "_").lower()
        city_data.to_csv(output_dir / f"{safe_city}_descriptions.csv", index=False)
    
    # Save just descriptions as text for easy reading
    with open(output_dir / "all_descriptions_only.txt", "w", encoding="utf-8") as f:
        for idx, row in df.iterrows():
            case_num = row.get('Case Number', 'N/A')
            city = row.get('city', 'N/A')
            address = row.get('Main Address', 'N/A')
            description = row[desc_col]
            
            f.write(f"City: {city} | Case: {case_num} | Address: {address}\n")
            f.write(f"Description: {description}\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"Descriptions saved to: {output_dir}")
    print(f"Files created:")
    print(f"  - all_descriptions.csv ({len(df)} records)")
    print(f"  - all_descriptions.parquet")
    print(f"  - all_descriptions_only.txt")
    if boca_df is not None:
        print(f"  - boca_raton_descriptions.csv ({len(boca_df)} records)")
        print(f"  - boca_raton_descriptions.parquet")
        print(f"  - boca_descriptions_only.txt")
    for city in df['city'].unique():
        safe_city = city.replace(" ", "_").lower()
        count = len(df[df['city'] == city])
        print(f"  - {safe_city}_descriptions.csv ({count} records)")

def search_descriptions(search_term):
    """Search for specific terms in descriptions."""
    
    df = extract_descriptions_from_csv()
    if df is None:
        return
    
    # Find the description column
    desc_cols = [col for col in df.columns if 'description' in col.lower()]
    if desc_cols:
        desc_col = desc_cols[0]
    elif 'Main Address' in df.columns:
        desc_col = 'Main Address'
    else:
        print("No description column found.")
        return
    
    # Search in descriptions (case-insensitive)
    mask = df[desc_col].astype(str).str.contains(search_term, case=False, na=False)
    matches = df[mask]
    
    print(f"\n🔍 Found {len(matches)} records matching '{search_term}':")
    print("-" * 60)
    
    for idx, row in matches.head(20).iterrows():  # Show first 20 matches
        case_num = row.get('Case Number', 'N/A')
        city = row.get('city', 'N/A')
        address = row.get('Main Address', 'N/A')
        description = row[desc_col]
        
        print(f"City: {city} | Case: {case_num}")
        print(f"Address: {address}")
        print(f"Description: {description}")
        print()
    
    if len(matches) > 20:
        print(f"... and {len(matches) - 20} more matches")

def search_boca_descriptions(search_term):
    """Search for specific terms in Boca Raton descriptions only."""
    
    boca_df = extract_boca_descriptions_only()
    if boca_df is None:
        return
    
    # Find the description column
    desc_cols = [col for col in boca_df.columns if 'description' in col.lower()]
    if desc_cols:
        desc_col = desc_cols[0]
    elif 'Main Address' in boca_df.columns:
        desc_col = 'Main Address'
    else:
        print("No description column found.")
        return
    
    # Search in descriptions (case-insensitive)
    mask = boca_df[desc_col].astype(str).str.contains(search_term, case=False, na=False)
    matches = boca_df[mask]
    
    print(f"\n🔍 Found {len(matches)} Boca Raton records matching '{search_term}':")
    print("-" * 60)
    
    for idx, row in matches.head(20).iterrows():  # Show first 20 matches
        case_num = row.get('Case Number', 'N/A')
        address = row.get('Main Address', 'N/A')
        description = row[desc_col]
        
        print(f"Case: {case_num}")
        print(f"Address: {address}")
        print(f"Description: {description}")
        print()
    
    if len(matches) > 20:
        print(f"... and {len(matches) - 20} more matches")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "extract":
            df = extract_descriptions_from_csv()
            if df is not None:
                print(f"\nSuccessfully extracted {len(df)} records with descriptions")
        
        elif command == "boca":
            boca_df = extract_boca_descriptions_only()
            if boca_df is not None:
                print(f"\nSuccessfully extracted {len(boca_df)} Boca Raton records with descriptions")
        
        elif command == "by-city":
            extract_descriptions_by_city()
        
        elif command == "save":
            save_boca_descriptions_to_file()
        
        elif command == "search" and len(sys.argv) > 2:
            search_term = " ".join(sys.argv[2:])
            search_descriptions(search_term)
        
        elif command == "search-boca" and len(sys.argv) > 2:
            search_term = " ".join(sys.argv[2:])
            search_boca_descriptions(search_term)
        
        else:
            print("Usage:")
            print("  python boca_extract_descriptions.py extract       - Extract and show summary")
            print("  python boca_extract_descriptions.py boca          - Extract Boca Raton only")
            print("  python boca_extract_descriptions.py by-city       - Show descriptions by city")
            print("  python boca_extract_descriptions.py save          - Save descriptions to files")
            print("  python boca_extract_descriptions.py search TERM   - Search for term in all descriptions")
            print("  python boca_extract_descriptions.py search-boca TERM - Search for term in Boca descriptions only")
    
    else:
        # Default: run Boca extraction and show summary
        boca_df = extract_boca_descriptions_only()
        if boca_df is not None:
            print(f"\n✅ Successfully extracted {len(boca_df)} Boca Raton records with descriptions")
            print("\nRun with arguments for more options:")
            print("  python boca_extract_descriptions.py by-city")
            print("  python boca_extract_descriptions.py save")
            print("  python boca_extract_descriptions.py search-boca 'graffiti'")
        else:
            # Fallback to all cities
            df = extract_descriptions_from_csv()
            if df is not None:
                print(f"\n✅ Successfully extracted {len(df)} total records with descriptions")
                print("No Boca Raton records found, but other cities available.")