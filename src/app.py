import streamlit as st
import pandas as pd
from pathlib import Path
from src.store import load_master, save_master
from src.clean import normalize
from src.ade_client import extract_pdf_bytes
from src.features import zone_aggregates, quick_address_score

st.set_page_config(page_title="CodeRisk SF", page_icon="📊", layout="wide")
st.title("CodeRisk SF — South Florida Code Violation Risk")

master = load_master()

tab1, tab2 = st.tabs(["📥 Upload PDFs (ADE)", "🧮 Quick Risk Score"])

with tab1:
    st.subheader("Upload violation PDFs → extract with ADE")
    schema_id = st.text_input("ADE Schema ID", value="", help="Enter the schema/template id you created in ADE")
    files = st.file_uploader("PDF files", type=["pdf"], accept_multiple_files=True)
    if st.button("Extract with ADE", disabled=not files or not schema_id):
        rows = []
        for f in files:
            try:
                out = extract_pdf_bytes(f.read(), schema_id)
                # Adjust to real ADE JSON structure
                for rec in out.get("records", []):
                    rows.append({
                        "city": rec.get("city"),
                        "address": rec.get("address"),
                        "zip": rec.get("zip"),
                        "date": rec.get("date"),
                        "violation_type": rec.get("violation_type"),
                        "fine_amount": rec.get("fine_amount"),
                        "contractor": rec.get("contractor"),
                    })
            except Exception as e:
                st.error(f"Failed {f.name}: {e}")

        if rows:
            new_df = normalize(pd.DataFrame(rows))
            master = pd.concat([master, new_df], ignore_index=True)
            save_master(master)
            st.success(f"Added {len(new_df)} rows. Master total: {len(master)}")
            st.dataframe(new_df.head(50), use_container_width=True)

    st.markdown("### Current dataset snapshot")
    st.dataframe(master.head(100), use_container_width=True)

with tab2:
    st.subheader("Address/Zone Risk Score")
    st.caption("Enter an address and zone (ZIP preferred, else city). Optionally, add known address violations in last 12 months.")

    col1, col2 = st.columns(2)
    with col1:
        zone = st.text_input("Zone (ZIP or City)", "")
        addr_cnt = st.number_input("Known address violations (last 12 months)", min_value=0, max_value=20, value=0)
    with col2:
        refresh = st.button("Recompute from data")

    data = master.copy()
    if refresh:
        st.toast("Recomputing aggregates…")
    if not data.empty:
        agg = zone_aggregates(data)
        st.markdown("#### Zone Leaderboard")
        st.dataframe(
            agg.sort_values("risk_score", ascending=False)
               .loc[:, ["zone","risk_score","percentile","cnt_90d","cnt_365d","repeat_ratio","fine_avg","sev_weighted"]]
               .head(25),
            use_container_width=True
        )
        if zone:
            res = quick_address_score(agg, zone, addr_cnt)
            if res["address_score"] is None:
                st.warning("Zone not found in current data.")
            else:
                st.metric("Zone risk score", f'{res["risk_zone_score"]:.3f}')
                st.metric("Zone percentile", f'{res["percentile"]:.0%}')
                st.metric("Address score", f'{res["address_score"]:.3f}')
    else:
        st.info("No master data yet. Upload PDFs in the first tab.")

st.markdown("---")
st.caption("Demo: ADE-powered extraction + explainable risk scoring for service providers, lenders, and investors.")
