# CodeRisk-SF

**Modular PDF Data Extraction & Normalization Pipeline for Code Violation Analysis**

A production-ready, scalable pipeline for extracting, cleaning, and consolidating code violation data from heterogeneous PDF reports across South Florida cities. Built with **LandingAI's Agentic Document Extraction (ADE)** and designed with enterprise-grade separation of concerns.

---

## 1. Architecture Overview

### **Modular Pipeline Design**
```
PDFs → 1_extraction.ipynb → cleaning/city_cleaning.ipynb → 3_consolidation.ipynb → Master Dataset
```

**🎯 Separation of Concerns:**
- **Extraction**: Generic PDF processing across all cities
- **Cleaning**: City-specific schema normalization  
- **Consolidation**: Unified master dataset creation

**📊 Supported Cities:**
- Boca Raton, Oakland Park, Pompano Beach
- Wilton Manors, Margate
- Extensible architecture for new cities

**🔧 Enterprise Features:**
- Raw data preservation for audit trails
- Resume capability for large datasets
- Standardized column schemas with `_raw` suffix
- Source file tracking for data lineage

---

## 2. Project Structure

```
coderisk-sf/
│
├── input_folder/                 # Raw PDFs by city
│   ├── bocaraton/
│   ├── oaklandpark/
│   ├── pompano/
│   ├── wiltonmanors/             # Official city name (plural)
│   └── margate/                  # New city support
│
├── results_folder/               # Extraction pipeline outputs
│   ├── bocaraton/
│   │   ├── raw_json/             # Preserved ADE JSON (audit trail)
│   │   └── tables/               # Raw CSV tables per PDF
│   └── [other cities...]/
│
├── clean_data/                   # Normalized city datasets
│   ├── bocaraton_clean.csv
│   ├── oaklandpark_clean.csv
│   └── master_violations.csv     # Consolidated dataset
│
├── cleaning/                     # City-specific cleaning notebooks
│   ├── bocaraton_cleaning.ipynb
│   └── [city]_cleaning.ipynb     # Template-based approach
│
├── src/                          # Core pipeline modules
│   ├── 1_extraction.ipynb        # Generic PDF extraction
│   ├── 3_consolidation.ipynb     # Master dataset creation
│   ├── ade_client.py             # LandingAI ADE wrapper
│   ├── normalizers.py            # City-specific schema mapping
│   ├── normalizer_dispatch.py    # City → normalizer routing
│   ├── utils.py                  # Data processing utilities  
│   └── __pycache__/
│
├── requirements.txt
├── .env                          # VISION_AGENT_API_KEY
└── README.md
```

---

## 3. Quick Start

### **1. Environment Setup**
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
```

### **2. API Configuration**
Create `.env` file in project root:
```
VISION_AGENT_API_KEY=your-landingai-api-key
```

### **3. Run the Pipeline**
```bash
# 1. Extract PDFs → Raw JSON + CSV tables
jupyter notebook src/1_extraction.ipynb

# 2. Clean city data → Standardized schemas  
jupyter notebook cleaning/bocaraton_cleaning.ipynb

# 3. Consolidate → Master dataset
jupyter notebook src/3_consolidation.ipynb
```

---

## 4. Pipeline Architecture

### **📁 Data Flow**
```
input_folder/city/file.pdf
    ↓ [1_extraction.ipynb]
results_folder/city/raw_json/file.json  +  results_folder/city/tables/file.csv
    ↓ [cleaning/city_cleaning.ipynb]  
clean_data/city_clean.csv
    ↓ [3_consolidation.ipynb]
clean_data/master_violations.csv
```

### **🏗️ Normalizer Architecture**
- **`normalizers.py`**: City-specific column mapping functions
- **`normalizer_dispatch.py`**: Smart city → normalizer routing
- **Standardized Schema**: All cities produce identical output columns:
  - `violation_id`, `violation_id_raw`
  - `parcel_number`, `parcel_number_raw` 
  - `city`, `source_file`, `address_raw`
  - Date fields: `opened_date_raw`, `closed_date_raw`
  - Status fields: `case_status_raw`, `violation_type_raw`

### **🔄 Resume Capability**
- Extraction automatically skips processed files
- Cleaning notebooks can incrementally process new extractions
- Full audit trail preserved in `raw_json/` folders

---

## 5. Supported Cities & Schema

### **🏙️ Current Cities**
| City | Normalizer Function | Schema Notes |
|------|-------------------|--------------|
| **Boca Raton** | `normalize_boca()` | Full ADE standard format |
| **Oakland Park** | `normalize_oakland()` | Shared with Boca (identical schema) |
| **Pompano Beach** | `normalize_pompano()` | Extended with days_active, actions |
| **Wilton Manors** | `normalize_wilton()` | Simplified schema |
| **Margate** | `normalize_margate()` | Combined fields (address+violation) |

### **🔧 Adding New Cities**
1. Add PDF folder: `input_folder/newcity/`
2. Create normalizer: `normalize_newcity()` in `normalizers.py`
3. Update dispatcher: Add `"newcity": "normalize_newcity"` mapping
4. Create cleaning notebook: `cleaning/newcity_cleaning.ipynb`

### **📋 Standard Output Schema**
Every city produces these columns:
```python
violation_id, violation_id_raw        # Unique case identifiers
parcel_number, parcel_number_raw      # Property identifiers (may be None)
city, source_file, address_raw        # Metadata and location
opened_date_raw, closed_date_raw      # Temporal data
case_status_raw, violation_type_raw   # Status information
```

---

## 6. Key Features

### **🎯 Production-Ready Design**
- **Separation of Concerns**: Extract → Clean → Consolidate
- **Data Lineage**: Every record traces back to source PDF + file
- **Schema Evolution**: Cities can change formats independently
- **Resume Support**: Skip already-processed files automatically

### **📊 Data Quality**
- **Raw Preservation**: Original data never lost (`_raw` suffix fields)
- **Validation**: Automatic data type coercion and date parsing
- **Deduplication**: Row-level hashing for duplicate detection
- **Missing Data**: Graceful handling of cities without parcel numbers

### **🔄 Scalability**
- **Template-Based**: New cities follow established patterns
- **Modular Processing**: Process one city or all cities
- **Incremental Updates**: Add new PDFs without reprocessing existing data

---

## 7. Technical Implementation

### **🔧 LandingAI ADE Integration**
```python
# src/ade_client.py - Clean wrapper around ADE SDK
from landingai_ade import LandingAIADE

ade_client = LandingAIADE(apikey=api_key)
parsed = ade_client.parse(pdf_path)        # Extract structured data
tables = extract_cases_df(parsed)          # Convert to DataFrame
```

### **🏗️ Normalizer Pattern**
```python
# src/normalizer_dispatch.py - Smart routing
normalizer = pick_normalizer("bocaraton")  # Returns normalize_boca()
clean_df = normalizer(raw_df, "bocaraton", "source_file.pdf")
```

### **📁 File Organization**
```
Per PDF: source.pdf → source.json + source.csv
Per City: city_clean.csv (all PDFs consolidated)  
Master: master_violations.csv (all cities unified)
```

---

## 8. Analytics Ready

### **📈 Ready for Analysis**
```python
import pandas as pd

# Load master dataset
df = pd.read_csv('clean_data/master_violations.csv')

# Violation frequency by city
df.groupby('city')['violation_id'].count()

# Missing parcel analysis
df[df['parcel_number'].isna()]['city'].value_counts()

# Temporal patterns
df['opened_date'] = pd.to_datetime(df['opened_date_raw'])
df.groupby([df['opened_date'].dt.year, 'city']).size()
```

### **🎯 Use Cases**
- **Risk Assessment**: Identify high-violation areas
- **Compliance Tracking**: Monitor case resolution times  
- **Resource Planning**: Understand enforcement patterns
- **Cross-City Comparison**: Benchmark violation rates

---

## 9. Dependencies

### **Core Requirements**
```
landingai-ade              # LandingAI Agentic Document Extraction
pandas>=2.0.0              # Data manipulation and analysis
python-dotenv              # Environment variable management
pathlib                    # Modern path handling (built-in)
jupyter                    # Notebook environment   
```

### **Optional Enhancements**
```
pyarrow                    # Parquet file support
openpyxl                   # Excel output support
```

---

## 10. Project Status

**🎯 LandingAI Financial Hack NYC 2025**

**Current Status**: Production-ready modular pipeline
- ✅ Generic extraction with resume capability
- ✅ City-specific normalization with schema standardization  
- ✅ Scalable architecture for new cities
- 🔄 Consolidation notebook (in development)

**Architecture Highlights**:
- Enterprise-grade separation of concerns
- Future-proof normalizer dispatch pattern
- Raw data preservation for audit trails
- Template-based extensibility for new cities