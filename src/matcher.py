# -*- coding: utf-8 -*-
"""
matcher.py – IMEI ve Baz İstasyonu Tabanlı Eşleştirme
"""

import pandas as pd
from .utils import seconds_to_timedelta, normalize_cell


def find_imei_overlaps(df: pd.DataFrame, tolerance_sec: int = 60) -> pd.DataFrame:
    if "IMEI" not in df.columns or df["IMEI"].dropna().empty:
        return pd.DataFrame()

    d = df.dropna(subset=["IMEI"]).copy()
    d = d.sort_values("DATETIME").reset_index(drop=True)

    overlaps = []
    tol = seconds_to_timedelta(tolerance_sec)

    for imei, grp in d.groupby("IMEI"):
        grp = grp.sort_values("DATETIME").reset_index(drop=True)
        n = len(grp)
        for i in range(n):
            for j in range(i + 1, n):
                if grp.loc[i, "MSISDN"] == grp.loc[j, "MSISDN"]:
                    continue
                t1 = grp.loc[i, "DATETIME"]
                t2 = grp.loc[j, "DATETIME"]
                diff = t2 - t1
                if abs(diff) <= tol:
                    overlaps.append({
                        "IMEI": imei,
                        "MSISDN_1": grp.loc[i, "MSISDN"],
                        "TIME_1": t1,
                        "CELL_1": grp.loc[i, "CELL"],
                        "FILE_1": grp.loc[i, "SOURCE_FILE"],
                        "MSISDN_2": grp.loc[j, "MSISDN"],
                        "TIME_2": t2,
                        "CELL_2": grp.loc[j, "CELL"],
                        "FILE_2": grp.loc[j, "SOURCE_FILE"],
                        "TIME_DIFF_SEC": int(abs(diff.total_seconds()))
                    })
                else:
                    if diff > tol:
                        break

    if not overlaps:
        return pd.DataFrame()

    return pd.DataFrame(overlaps).sort_values("TIME_1").reset_index(drop=True)


def find_cell_overlaps(df: pd.DataFrame, tolerance_sec: int = 300) -> pd.DataFrame:
    if "CELL" not in df.columns or df["CELL"].dropna().empty:
        return pd.DataFrame()

    d = df.dropna(subset=["CELL"]).copy()
    d["CELL_NORM"] = d["CELL"].apply(normalize_cell)
    d = d.sort_values("DATETIME").reset_index(drop=True)

    overlaps = []
    tol = seconds_to_timedelta(tolerance_sec)

    for cell_id, grp in d.groupby("CELL_NORM"):
        grp = grp.sort_values("DATETIME").reset_index(drop=True)
        n = len(grp)
        for i in range(n):
            t1 = grp.loc[i, "DATETIME"]
            for j in range(i + 1, n):
                if grp.loc[i, "MSISDN"] == grp.loc[j, "MSISDN"]:
                    continue
                t2 = grp.loc[j, "DATETIME"]
                diff = t2 - t1
                if abs(diff) <= tol:
                    overlaps.append({
                        "CELL_ID": cell_id,
                        "MSISDN_1": grp.loc[i, "MSISDN"],
                        "TIME_1": t1,
                        "IMEI_1": grp.loc[i, "IMEI"],
                        "FILE_1": grp.loc[i, "SOURCE_FILE"],
                        "MSISDN_2": grp.loc[j, "MSISDN"],
                        "TIME_2": t2,
                        "IMEI_2": grp.loc[j, "IMEI"],
                        "FILE_2": grp.loc[j, "SOURCE_FILE"],
                        "TIME_DIFF_SEC": int(abs(diff.total_seconds())),
                        "CELL_RAW_1": grp.loc[i, "CELL"],
                        "CELL_RAW_2": grp.loc[j, "CELL"],
                    })
                else:
                    if diff > tol:
                        break

    if not overlaps:
        return pd.DataFrame()

    return pd.DataFrame(overlaps).sort_values("TIME_1").reset_index(drop=True)
