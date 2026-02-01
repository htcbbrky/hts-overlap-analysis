# -*- coding: utf-8 -*-
"""
reporter.py – Raporlama ve Özet Çıktılar
"""

import os
import pandas as pd
from .utils import ensure_dir


def export_reports(all_df: pd.DataFrame,
                   imei_overlaps: pd.DataFrame | None,
                   cell_overlaps: pd.DataFrame | None,
                   out_dir: str):
    ensure_dir(out_dir)

    all_path_xlsx = os.path.join(out_dir, "hts_merged_all.xlsx")
    all_path_csv = os.path.join(out_dir, "hts_merged_all.csv")
    all_df.to_excel(all_path_xlsx, index=False)
    all_df.to_csv(all_path_csv, index=False, encoding="utf-8-sig")

    if imei_overlaps is not None and not imei_overlaps.empty:
        imei_xlsx = os.path.join(out_dir, "imei_overlap_report.xlsx")
        imei_csv = os.path.join(out_dir, "imei_overlap_report.csv")
        imei_overlaps.to_excel(imei_xlsx, index=False)
        imei_overlaps.to_csv(imei_csv, index=False, encoding="utf-8-sig")

    if cell_overlaps is not None and not cell_overlaps.empty:
        cell_xlsx = os.path.join(out_dir, "cell_overlap_report.xlsx")
        cell_csv = os.path.join(out_dir, "cell_overlap_report.csv")
        cell_overlaps.to_excel(cell_xlsx, index=False)
        cell_overlaps.to_csv(cell_csv, index=False, encoding="utf-8-sig")


def print_summary(all_df: pd.DataFrame,
                  imei_overlaps: pd.DataFrame | None,
                  cell_overlaps: pd.DataFrame | None):
    print("\n=== HTS OVERLAP ANALİZ ÖZETİ ===")
    print(f"Toplam kayıt sayısı: {len(all_df)}")
    print(f"Toplam hat (MSISDN) sayısı: {all_df['MSISDN'].nunique()}")

    if "IMEI" in all_df.columns:
        print(f"Toplam IMEI sayısı: {all_df['IMEI'].dropna().nunique()}")
    if "CELL" in all_df.columns:
        print(f"Toplam baz istasyonu kaydı: {all_df['CELL'].dropna().nunique()}")

    print("\n- IMEI overlap tespiti -")
    if imei_overlaps is None or imei_overlaps.empty:
        print("  Herhangi bir IMEI overlap kaydı bulunamadı.")
    else:
        print(f"  Tespit edilen IMEI overlap olayı: {len(imei_overlaps)}")
        print(imei_overlaps.head(10).to_string(index=False))

    print("\n- Baz istasyonu (CELL) overlap tespiti -")
    if cell_overlaps is None or cell_overlaps.empty:
        print("  Herhangi bir baz istasyonu overlap kaydı bulunamadı.")
    else:
        print(f"  Tespit edilen CELL overlap olayı: {len(cell_overlaps)}")
        print(cell_overlaps.head(10).to_string(index=False))

    print("\nAnaliz tamamlandı.\n")
