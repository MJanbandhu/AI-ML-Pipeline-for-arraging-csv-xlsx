# app.py
import io
import difflib
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data Format Alignment", layout="wide")

def _normalize(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = " ".join(s.replace("_", " ").replace("-", " ").split())
    return "".join(ch for ch in s if ch.isalnum() or ch.isspace())

def best_match(target: str, candidates: list[str], cutoff: float) -> str | None:
    norm_map = {_normalize(c): c for c in candidates}
    t = _normalize(target)
    if t in norm_map:
        return norm_map[t]
    hits = difflib.get_close_matches(t, list(norm_map.keys()), n=1, cutoff=cutoff)
    return norm_map[hits[0]] if hits else None

def read_any(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    data = uploaded_file.read()
    if name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(data))
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(io.BytesIO(data))
    raise ValueError("Unsupported file format. Use CSV or Excel.")

def build_mapping(schema_cols: list[str], data2_cols: list[str], cutoff: float) -> dict[str, str | None]:
    mapping = {}
    for c in schema_cols:
        mapping[c] = best_match(c, data2_cols, cutoff)
    return mapping

def align(df_schema: pd.DataFrame, df_data2: pd.DataFrame, mapping: dict[str, str | None]) -> pd.DataFrame:
    out = pd.DataFrame(columns=list(df_schema.columns))
    for col in df_schema.columns:
        src = mapping.get(col)
        out[col] = df_data2[src] if src and src in df_data2.columns else np.nan
    return out

st.title("AI/ML Data Format Alignment Pipeline")

st.markdown(
    "Upload data1 (schema) and data2 (content). The app will map data2 into the exact column order of data1. "
    "You can adjust the similarity threshold and override the suggested mapping if necessary."
)

with st.sidebar:
    st.header("Settings")
    cutoff = st.slider("Similarity threshold", min_value=0.0, max_value=1.0, value=0.6, step=0.05)
    output_fmt = st.selectbox("Output format", ["CSV", "Excel"])

col1, col2 = st.columns(2)
with col1:
    up1 = st.file_uploader("Upload data1 (schema)", type=["csv","xlsx","xls"], key="data1")
with col2:
    up2 = st.file_uploader("Upload data2 (content)", type=["csv","xlsx","xls"], key="data2")

if up1 is not None and up2 is not None:
    try:
        df1 = read_any(up1)
        df2 = read_any(up2)
    except Exception as e:
        st.error(f"File read error: {e}")
        st.stop()

    st.success(f"Files loaded. data1 shape: {df1.shape} | data2 shape: {df2.shape}")

    suggested = build_mapping(list(df1.columns), list(df2.columns), cutoff)

    st.subheader("Suggested column mapping (data1 → data2)")
    map_df = pd.DataFrame(
        {"data1_column": list(df1.columns),
         "suggested_data2_source": [suggested[c] if suggested[c] is not None else "" for c in df1.columns]}
    )
    st.dataframe(map_df, use_container_width=True)

    st.subheader("Adjust mapping if needed")
    override_mapping = {}
    for col in df1.columns:
        options = [""] + list(df2.columns)
        default = suggested[col] if suggested[col] in df2.columns else ""
        override_mapping[col] = st.selectbox(f"{col}", options=options, index=options.index(default) if default in options else 0)

    final_mapping = {k: (v if v != "" else None) for k, v in override_mapping.items()}

    aligned = align(df1, df2, final_mapping)

    st.subheader("Preview of aligned data (first 20 rows)")
    st.dataframe(aligned.head(20), use_container_width=True)

    if output_fmt == "CSV":
        csv_bytes = aligned.to_csv(index=False).encode("utf-8")
        st.download_button("Download outputdata.csv", data=csv_bytes, file_name="outputdata.csv", mime="text/csv")
    else:
        bio = io.BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
            aligned.to_excel(writer, index=False, sheet_name="outputdata")
        bio.seek(0)
        st.download_button("Download outputdata.xlsx", data=bio, file_name="outputdata.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.info("Please upload both data1 and data2 to proceed.")
