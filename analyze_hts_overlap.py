#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTS Overlap Analysis – Ana Script

Amaç:
- Farklı GSM hatlarına ait HTS kayıtlarını (Excel/CSV) okuyup tek bir veri havuzunda toplar.
- Aynı zaman aralığında, aynı/benzer baz istasyonu ya da aynı/benzer IMEI ile
  birden fazla hattın eşzamanlı kullanımını (overlap) tespit eder.
- Özellikle:
    * Aynı IMEI, farklı hatlar (SIM swap / hat değişimi şüphesi)
    * Aynı hücre (Cell ID / Baz istasyonu), kısa zaman farkı, farklı hatlar
      (aynı fiziki konumda bir arada olma şüphesi)
- Çıktıyı hem ekrana özet olarak hem de Excel/CSV dosyalarına detaylı olarak üretir.

Not:
- Bu script, delil toplama/analiz amacıyla, CMK m.135 ve ilgili BTK kayıtları
  çerçevesinde teknik rapor hazırlanmasına yardımcı olacak şekilde kurgulanmıştır.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# KULLANICI TARAFINDAN DÜZENLENECEK TEMEL PARAMETRELER
# ---------------------------------------------------------------------------

# HTS dosyalarının bulunduğu klasör (Excel/CSV)
DATA_DIR = "data/hts"  # örnek: "data/hts"

# Çıktıların yazılacağı klasör
OUTPUT_DIR = "output/hts_overlap"

# Analize dahil edilecek dosya uzantıları
ALLOWED_EXTENSIONS = [".xlsx", ".xls", ".csv"]

# Tarih ve saat sütunu isimleri (dosyalardaki kolon adlarına göre uyarlayın)
DATE_COL = "TARIH"
TIME_COL = "SAAT"

# Hat (MSISDN) sütunu
MSISDN_COL = "NUMARA"

# IMEI sütunu (varsa)
IMEI_COL = "IMEI"

# Baz istasyonu / Hücre bilgisi sütunu (BTK raporlarında genelde istasyon açıklaması)
CELL_COL = "BAZ_ISTASYONU"  # gerekirse orijinal başlığa göre değiştirin

# Zaman çözünürlüğü ve tolerans ayarları
# Aynı IMEI için farklı hatların eşzamanlı kullanımı tespiti için tolerans (saniye)
IMEI_OVERLAP_TOLERANCE_SEC = 60

# Aynı/benzer baz istasyonu için farklı hatların co-location tespiti toleransı (saniye)
CELL_OVERLAP_TOLERANCE_SEC = 300

# Overlap analizi sadece şu hatlar arasında mı yapılacak?
# Ör: ["5384490510", "5378479523", "5327670070"] veya boş liste => tüm hatlar
FOCUS_MSISDNS = []


# ---------------------------------------------------------------------------
# YARDIMCI FONKSİYONLAR
# ---------------------------------------------------------------------------

def list_input_files(data_dir: str, extensions=None):
    """Klasördeki uygun uzantılı dosyaları listeler."""
    if extensions is None:
        extensions = ALLOWED_EXTENSIONS
    files = []
    for root, _, filenames in os.walk(data_dir):
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in extensions:
                files.append(os.path.join(root, fn))
    return files


def read_hts_file(path: str) -> pd.DataFrame:
    """
    Tek bir HTS dosyasını okur ve standart kolonlara dönüştürür.
    - Tarih + Saat => DATETIME
    - Kolon adlarını normalize eder (büyük/küçük farkını giderir).
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    elif ext == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Desteklenmeyen dosya uzantısı: {path}")

    # Kolon adlarını normalize (büyük/küçük harf)
    df.columns = [str(c).strip().upper() for c in df.columns]

    # Gerekli kolonları bulma
    def find_col(possible_names):
        for name in possible_names:
            up = name.upper()
            if up in df.columns:
                return up
        return None

    date_col = find_col([DATE_COL, "TARIH", "DATE"])
    time_col = find_col([TIME_COL, "SAAT", "TIME"])
    msisdn_col = find_col([MSISDN_COL, "NUMARA", "MSISDN", "ABONE_NUMARASI"])
    imei_col = find_col([IMEI_COL, "IMEI", "CAGRI_YON_IMEI"])
    cell_col = find_col([CELL_COL, "BAZ_ISTASYONU", "HUC_RE_ADI", "CELL", "ISTASYON"])

    # Eksik temel kolonlar varsa hata vermeden boş geçelim (rapor türü farklı olabilir)
    if date_col is None or time_col is None or msisdn_col is None:
        # Boş DataFrame dönelim (analize dahil etmeyiz)
        return pd.DataFrame(columns=[
            "DATETIME", "MSISDN", "IMEI", "CELL", "SOURCE_FILE"
        ])

    # Tarih + Saat birleştirme
    def parse_datetime(row):
        d = str(row[date_col]).strip()
        t = str(row[time_col]).strip()
        if not d or d.lower() in ["nan", "none"]:
            return pd.NaT
        # BTK rapor formatlarına göre birkaç olası biçimi deneyelim
        for fmt in ("%d.%m.%Y %H%M%S", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(f"{d} {t}", fmt)
            except Exception:
                continue
        return pd.NaT

    df["DATETIME"] = df.apply(parse_datetime, axis=1)

    # Standart kolon isimleri
    out = pd.DataFrame()
    out["DATETIME"] = df["DATETIME"]
    out["MSISDN"] = df[msisdn_col].astype(str).str.strip() if msisdn_col else None
    out["IMEI"] = df[imei_col].astype(str).str.strip() if imei_col else None
    out["CELL"] = df[cell_col].astype(str).str.strip() if cell_col else None
    out["SOURCE_FILE"] = os.path.basename(path)

    # Tarihi olmayan kayıtları at
    out = out.dropna(subset=["DATETIME"])
    return out


def load_all_hts(data_dir: str) -> pd.DataFrame:
    """Tüm HTS dosyalarını okuyup tek DataFrame’de birleştirir."""
    files = list_input_files(data_dir)
    all_dfs = []
    for path in files:
        try:
            df = read_hts_file(path)
            if not df.empty:
                all_dfs.append(df)
        except Exception as e:
            print(f"[UYARI] Dosya okunamadı: {path} - Hata: {e}", file=sys.stderr)
    if not all_dfs:
        return pd.DataFrame(columns=["DATETIME", "MSISDN", "IMEI", "CELL", "SOURCE_FILE"])
    big = pd.concat(all_dfs, ignore_index=True)
    # Zaman sıralaması
    big = big.sort_values("DATETIME").reset_index(drop=True)

    # Belirli hatlara odaklanılacaksa filtrele
    if FOCUS_MSISDNS:
        big = big[big["MSISDN"].isin(FOCUS_MSISDNS)].reset_index(drop=True)

    return big


# ---------------------------------------------------------------------------
# OVERLAP ANALİZ FONKSİYONLARI
# ---------------------------------------------------------------------------

def find_imei_overlaps(df: pd.DataFrame, tolerance_sec: int = 60) -> pd.DataFrame:
    """
    Aynı IMEI'yi kullanan farklı MSISDN'lerin, tolerans dahilinde zaman
    olarak çakışmalarını tespit eder.
    """
    if "IMEI" not in df.columns or df["IMEI"].dropna().empty:
        return pd.DataFrame()

    # Sadece IMEI dolu kayıtlar
    d = df.dropna(subset=["IMEI"]).copy()
    d = d.sort_values("DATETIME").reset_index(drop=True)

    overlaps = []
    tol = timedelta(seconds=tolerance_sec)

    # Aynı IMEI grupları üzerinden ilerle
    for imei, grp in d.groupby("IMEI"):
        grp = grp.sort_values("DATETIME").reset_index(drop=True)
        # İki farklı MSISDN'li kayıt arasında zaman farkına bak
        n = len(grp)
        for i in range(n):
            for j in range(i + 1, n):
                # Farklı hatlar mı?
                if grp.loc[i, "MSISDN"] == grp.loc[j, "MSISDN"]:
                    continue
                t1 = grp.loc[i, "DATETIME"]
                t2 = grp.loc[j, "DATETIME"]
                if abs(t2 - t1) <= tol:
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
                        "TIME_DIFF_SEC": int(abs((t2 - t1).total_seconds()))
                    })
                else:
                    # Grup zaman sıralı olduğundan, daha sonraki kayıtlar için fark artacaktır
                    if t2 - t1 > tol:
                        break

    if not overlaps:
        return pd.DataFrame()

    return pd.DataFrame(overlaps).sort_values("TIME_1").reset_index(drop=True)


def normalize_cell(cell_str: str) -> str:
    """
    Baz istasyonu/Cell açıklamasını normalize eder (ör: sadece ID kısmını alma).
    BTK raporlarında istasyon açıklaması çok uzun olabilir; burada sadeleştirme
    için basit bir yaklaşım kullanıyoruz.
    """
    if not isinstance(cell_str, str):
        return ""
    s = cell_str.strip()
    # Örnek: "43783593007 - oprTurkcellISTHOJ4L - ISTANBUL ..." => "43783593007"
    if "-" in s:
        first = s.split("-")[0].strip()
        return first
    return s


def find_cell_overlaps(df: pd.DataFrame, tolerance_sec: int = 300) -> pd.DataFrame:
    """
    Aynı/benzer baz istasyonu (CELL) içinde, tolerans dahilinde
    farklı MSISDN'lerin co-location şüphesini tespit eder.
    """
    if "CELL" not in df.columns or df["CELL"].dropna().empty:
        return pd.DataFrame()

    d = df.dropna(subset=["CELL"]).copy()
    d["CELL_NORM"] = d["CELL"].apply(normalize_cell)
    d = d.sort_values("DATETIME").reset_index(drop=True)

    overlaps = []
    tol = timedelta(seconds=tolerance_sec)

    for cell_id, grp in d.groupby("CELL_NORM"):
        grp = grp.sort_values("DATETIME").reset_index(drop=True)
        n = len(grp)
        for i in range(n):
            t1 = grp.loc[i, "DATETIME"]
            for j in range(i + 1, n):
                # Farklı hatlar mı?
                if grp.loc[i, "MSISDN"] == grp.loc[j, "MSISDN"]:
                    continue
                t2 = grp.loc[j, "DATETIME"]
                if abs(t2 - t1) <= tol:
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
                        "TIME_DIFF_SEC": int(abs((t2 - t1).total_seconds())),
                        "CELL_RAW_1": grp.loc[i, "CELL"],
                        "CELL_RAW_2": grp.loc[j, "CELL"],
                    })
                else:
                    if t2 - t1 > tol:
                        break

    if not overlaps:
        return pd.DataFrame()

    return pd.DataFrame(overlaps).sort_values("TIME_1").reset_index(drop=True)


# ---------------------------------------------------------------------------
# RAPORLAMA FONKSİYONLARI
# ---------------------------------------------------------------------------

def ensure_output_dir(path: str):
    os.makedirs(path, exist_ok=True)


def export_reports(all_df: pd.DataFrame,
                   imei_overlaps: pd.DataFrame,
                   cell_overlaps: pd.DataFrame,
                   out_dir: str):
    """Analiz sonuçlarını Excel ve CSV olarak dışa aktarır."""
    ensure_output_dir(out_dir)

    # Ham birleşik veriyi kaydet
    all_path_xlsx = os.path.join(out_dir, "hts_merged_all.xlsx")
    all_path_csv = os.path.join(out_dir, "hts_merged_all.csv")
    all_df.to_excel(all_path_xlsx, index=False)
    all_df.to_csv(all_path_csv, index=False, encoding="utf-8-sig")

    # IMEI overlap raporu
    if not imei_overlaps.empty:
        imei_xlsx = os.path.join(out_dir, "imei_overlap_report.xlsx")
        imei_csv = os.path.join(out_dir, "imei_overlap_report.csv")
        imei_overlaps.to_excel(imei_xlsx, index=False)
        imei_overlaps.to_csv(imei_csv, index=False, encoding="utf-8-sig")

    # Cell overlap raporu
    if not cell_overlaps.empty:
        cell_xlsx = os.path.join(out_dir, "cell_overlap_report.xlsx")
        cell_csv = os.path.join(out_dir, "cell_overlap_report.csv")
        cell_overlaps.to_excel(cell_xlsx, index=False)
        cell_overlaps.to_csv(cell_csv, index=False, encoding="utf-8-sig")


def print_summary(all_df: pd.DataFrame,
                  imei_overlaps: pd.DataFrame,
                  cell_overlaps: pd.DataFrame):
    """Kısa metin özetini stdout'a yazar."""
    print("\n=== HTS OVERLAP ANALİZ ÖZETİ ===")
    print(f"Toplam kayıt sayısı: {len(all_df)}")
    print(f"Toplam hat (MSISDN) sayısı: {all_df['MSISDN'].nunique()}")
    if "IMEI" in all_df.columns:
        print(f"Toplam IMEI sayısı: {all_df['IMEI'].dropna().nunique()}")
    if "CELL" in all_df.columns:
        print(f"Toplam baz istasyonu kaydı: {all_df['CELL'].dropna().nunique()}")

    print("\n- IMEI overlap tespiti -")
    if imei_overlaps.empty:
        print("  Herhangi bir IMEI overlap kaydı bulunamadı.")
    else:
        print(f"  Tespit edilen IMEI overlap olayı: {len(imei_overlaps)}")
        # İlk birkaç olayı göster
        print(imei_overlaps.head(10).to_string(index=False))

    print("\n- Baz istasyonu (CELL) overlap tespiti -")
    if cell_overlaps.empty:
        print("  Herhangi bir baz istasyonu overlap kaydı bulunamadı.")
    else:
        print(f"  Tespit edilen CELL overlap olayı: {len(cell_overlaps)}")
        print(cell_overlaps.head(10).to_string(index=False))

    print("\nAnaliz tamamlandı.\n")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print(f"HTS dosyaları klasörü: {DATA_DIR}")
    print(f"Çıktı klasörü: {OUTPUT_DIR}")

    all_df = load_all_hts(DATA_DIR)
    if all_df.empty:
        print("Analize uygun HTS kaydı bulunamadı. Lütfen klasör ve kolon adlarını kontrol edin.")
        return

    # IMEI overlap analizi
    imei_overlaps = find_imei_overlaps(all_df, tolerance_sec=IMEI_OVERLAP_TOLERANCE_SEC)

    # Baz istasyonu overlap analizi
    cell_overlaps = find_cell_overlaps(all_df, tolerance_sec=CELL_OVERLAP_TOLERANCE_SEC)

    # Raporları dışa aktar
    export_reports(all_df, imei_overlaps, cell_overlaps, OUTPUT_DIR)

    # Konsol özeti
    print_summary(all_df, imei_overlaps, cell_overlaps)


if __name__ == "__main__":
    main()

