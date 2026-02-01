# -*- coding: utf-8 -*-
"""
analyzer.py – Yüksek Seviyeli Analiz Akışı
"""

import pandas as pd
from .parser import load_all_hts
from .matcher import find_imei_overlaps, find_cell_overlaps


class HTSAnalyzer:
    def __init__(self,
                 data_dir: str,
                 focus_msisdns=None,
                 imei_tol_sec: int = 60,
                 cell_tol_sec: int = 300):
        self.data_dir = data_dir
        self.focus_msisdns = focus_msisdns or []
        self.imei_tol_sec = imei_tol_sec
        self.cell_tol_sec = cell_tol_sec

        self.all_df: pd.DataFrame | None = None
        self.imei_overlaps: pd.DataFrame | None = None
        self.cell_overlaps: pd.DataFrame | None = None

    def load(self):
        self.all_df = load_all_hts(self.data_dir, self.focus_msisdns)

    def run_imei_analysis(self):
        if self.all_df is None:
            raise RuntimeError("Önce load() çağrılmalı.")
        self.imei_overlaps = find_imei_overlaps(self.all_df, tolerance_sec=self.imei_tol_sec)

    def run_cell_analysis(self):
        if self.all_df is None:
            raise RuntimeError("Önce load() çağrılmalı.")
        self.cell_overlaps = find_cell_overlaps(self.all_df, tolerance_sec=self.cell_tol_sec)

    def run_all(self):
        self.load()
        self.run_imei_analysis()
        self.run_cell_analysis()
        return self.all_df, self.imei_overlaps, self.cell_overlaps
