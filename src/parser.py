# -*- coding: utf-8 -*-
"""
parser.py – HTS Dosya Okuyucu ve Normalleştirici
"""

import os
from datetime import datetime
import pandas as pd

ALLOWED_EXTENSIONS = [".xlsx", ".xls", ".csv"]

# Varsayılan kolon isimleri (ana script ile uyumlu olmalı)
DATE_COLS = ["TARIH", "DATE"]
TIME_COLS = ["SAAT", "TIME"]
MSISDN_COLS = ["NUMARA", "MSISDN", "ABONE_NUMARASI"]
IMEI_COLS = ["IMEI", "CAGRI_YON_IMEI"]
CELL_COLS = ["BAZ_ISTASYONU", "HUC_RE_ADI", "CELL", "ISTASYON"]


def list_input_files(data_dir: str, extensions=None):
    if extensions is None:
        extensions = ALLOWED_EXTENSIONS
    files = []
    for root, _, filenames in os.walk(data_dir):
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in extensions:
                files.append(os.path.join(root, fn))
    return files


def _find_col(df: pd.DataFrame, candidates):
    cols = [str(c).strip().upper() for c in df.columns]
    for name in candidates:
        up = name.upper()
        if up in cols:
            # orijinal ismi döndür
            return df.columns[cols.index(up)]
    return None


def _parse_datetime(row, date_col, time_col):
    d = str(row[date_col]).strip()
    t = str(row[time_col]).strip()
    if not d or d.lower() in ["nan", "none"]:
        return pd.NaT
    for fmt in ("%d.%m.%Y %H%M%S", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(f"{d} {t}", fmt)
        except Exception:
            continue
    return pd.NaT


def read_hts_file(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    elif ext == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Desteklenmeyen dosya uzantısı: {path}")

    date_col = _find_col(df, DATE_COLS)
    time_col = _find_col(df, TIME_COLS)
    msisdn_col = _find_col(df, MSISDN_COLS)
    imei_col = _find_col(df, IMEI_COLS)
    cell_col = _find_col(df, CELL_COLS)

    if date_col is None or time_col is None or msisdn_col is None:
        return pd.DataFrame(columns=["DATETIME", "MSISDN", "IMEI", "CELL", "SOURCE_FILE"])

    df["DATETIME"] = df.apply(_parse_datetime, axis=1, args=(date_col, time_col))

    out = pd.DataFrame()
    out["DATETIME"] = df["DATETIME"]
    out["MSISDN"] = df[msisdn_col].astype(str).str.strip()
    out["IMEI"] = df[imei_col].astype(str).str.strip() if imei_col else None
    out["CELL"] = df[cell_col].astype(str).str.strip() if cell_col else None
    out["SOURCE_FILE"] = os.path.basename(path)

    out = out.dropna(subset=["DATETIME"])
    return out


def load_all_hts(data_dir: str, focus_msisdns=None) -> pd.DataFrame:
    files = list_input_files(data_dir)
    all_dfs = []
    for path in files:
        try:
            df = read_hts_file(path)
            if not df.empty:
                all_dfs.append(df)
        except Exception:
            continue
    if not all_dfs:
        return pd.DataFrame(columns=["DATETIME", "MSISDN", "IMEI", "CELL", "SOURCE_FILE"])
    big = pd.concat(all_dfs, ignore_index=True)
    big = big.sort_values("DATETIME").reset_index(drop=True)

    if focus_msisdns:
        big = big[big["MSISDN"].isin(focus_msisdns)].reset_index(drop=True)

    return big

