import pandas as pd
import numpy as np
import streamlit as st

from .config import SM3_TO_BBL, SM3_TO_MSCF


def _format_well_name(raw: str) -> str:
    name = raw.replace("_", " ")
    parts = name.split("-")
    if len(parts) >= 2:
        name = parts[0] + "/" + parts[1] + "-" + "-".join(parts[2:])
    return name.strip()


def load_excel_production(file) -> dict:
    xl = pd.ExcelFile(file)
    wells = {}
    for sheet in xl.sheet_names:
        if "index" in sheet.lower() or "summary" in sheet.lower():
            continue
        raw = None
        for header_row in [0, 1, 2]:
            try:
                raw = xl.parse(sheet, header=header_row)
                if len(raw.columns) > 1:
                    break
            except Exception:
                continue
        if raw is None or len(raw.columns) < 2:
            continue
        raw.columns = raw.columns.astype(str).str.strip().str.lower()
        col_map = {}
        oil_already_bbl = False
        gas_is_mmscf = False
        gas_already_mscf = False
        for col in raw.columns:
            if any(x in col for x in ["date", "time", "periode", "start date"]):
                col_map[col] = "Date"
            elif any(x in col for x in ["oil rate", "oil prod", "crude oil", "daily oil"]):
                col_map[col] = "Oil_Sm3"
                oil_already_bbl = "bbl" in col
            elif any(x in col for x in ["gas rate", "gas prod", "dry gas", "daily gas"]):
                col_map[col] = "Gas_Sm3"
                gas_is_mmscf = "mmscf" in col
                gas_already_mscf = "mscf" in col and "mmscf" not in col
            elif any(x in col for x in ["water rate", "water prod", "produced water", "daily water"]):
                col_map[col] = "Water_Sm3"
            elif any(x in col for x in ["on-stream", "onstream", "on stream", "hrs", "hours", "uptime", "operating"]):
                col_map[col] = "OnStreamHrs"
        raw = raw.rename(columns=col_map)
        available = [c for c in ["Date", "Oil_Sm3", "Gas_Sm3", "Water_Sm3", "OnStreamHrs"] if c in raw.columns]
        if "Date" not in available or "Oil_Sm3" not in available:
            st.warning(f"⚠️ Sheet '{sheet}': Missing Date or Oil columns. Skipping.")
            continue
        df = raw[available].copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df[df["Date"].notna()].copy()
        if len(df) < 6:
            st.warning(f"⚠️ Sheet '{sheet}': Only {len(df)} valid date rows. Skipping.")
            continue
        for col in ["Oil_Sm3", "Gas_Sm3", "Water_Sm3", "OnStreamHrs"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        df = df[df["Oil_Sm3"] > 0].copy()
        if "OnStreamHrs" in df.columns:
            if (df["OnStreamHrs"] > 0).any():
                df = df[(df["OnStreamHrs"] > 0) & (df["OnStreamHrs"] <= 24)].copy()
        if len(df) < 6:
            st.warning(f"⚠️ Sheet '{sheet}': Insufficient valid production data ({len(df)} rows). Skipping.")
            continue
        df["Oil_bbl"] = df["Oil_Sm3"] if oil_already_bbl else df["Oil_Sm3"] * SM3_TO_BBL
        gas_src = df.get("Gas_Sm3", pd.Series(0.0, index=df.index))
        if gas_is_mmscf:
            df["Gas_mscf"] = gas_src * 1000.0
        elif gas_already_mscf:
            df["Gas_mscf"] = gas_src
        else:
            df["Gas_mscf"] = gas_src * SM3_TO_MSCF
        df["Water_bbl"] = df.get("Water_Sm3", pd.Series(0.0, index=df.index)) * SM3_TO_BBL
        df = df.sort_values("Date").reset_index(drop=True)
        wells[_format_well_name(sheet)] = df
    return wells


def load_csv_production(file) -> dict:
    try:
        df = pd.read_csv(file)
    except Exception as e:
        st.error(f"CSV read error: {e}")
        return {}
    if df.empty:
        st.error("CSV file is empty.")
        return {}
    df.columns = df.columns.astype(str).str.strip().str.lower()
    col_map = {}
    for col in df.columns:
        if any(x in col for x in ["date", "time", "periode", "start date"]):
            col_map[col] = "Date"
        elif col in ("well", "wellname", "well_name", "wellid"):
            col_map[col] = "Well"
        elif any(x in col for x in ["oil rate", "oil prod", "crude oil", "daily oil", "oil"]):
            col_map[col] = "Oil_Sm3"
        elif any(x in col for x in ["gas rate", "gas prod", "dry gas", "daily gas", "gas"]):
            col_map[col] = "Gas_Sm3"
        elif any(x in col for x in ["water rate", "water prod", "produced water", "daily water", "water", "wtr"]):
            col_map[col] = "Water_Sm3"
        elif any(x in col for x in ["on-stream", "onstream", "on stream", "hrs", "hours", "uptime", "operating"]):
            col_map[col] = "OnStreamHrs"
    df = df.rename(columns=col_map)
    if "Date" not in df.columns or "Oil_Sm3" not in df.columns:
        st.error("CSV must contain 'date' and 'oil' columns.")
        return {}
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    initial_rows = len(df)
    df = df[df["Date"].notna()].copy()
    for col in ["Oil_Sm3", "Gas_Sm3", "Water_Sm3", "OnStreamHrs"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    max_oil = df["Oil_Sm3"].max()
    if max_oil > 2000:
        df["Oil_bbl"] = df["Oil_Sm3"] * SM3_TO_BBL
        df["Gas_mscf"] = df.get("Gas_Sm3", pd.Series(0.0, index=df.index)) * SM3_TO_MSCF
        df["Water_bbl"] = df.get("Water_Sm3", pd.Series(0.0, index=df.index)) * SM3_TO_BBL
    else:
        df["Oil_bbl"] = df["Oil_Sm3"]
        df["Gas_mscf"] = df.get("Gas_Sm3", pd.Series(0.0, index=df.index))
        df["Water_bbl"] = df.get("Water_Sm3", pd.Series(0.0, index=df.index))
    wells = {}
    if "Well" in df.columns:
        for well, grp in df.groupby("Well"):
            well_name = str(well).strip()
            well_df = grp[grp["Oil_bbl"] > 0].sort_values("Date").reset_index(drop=True)
            if len(well_df) >= 10:
                wells[well_name] = well_df
    else:
        df_clean = df[df["Oil_bbl"] > 0].sort_values("Date").reset_index(drop=True)
        if len(df_clean) >= 10:
            wells["Well-01"] = df_clean
    if not wells:
        st.warning(f"No valid production data found. Processed {initial_rows} rows, but none met quality criteria.")
    return wells
