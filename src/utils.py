# -*- coding: utf-8 -*-
"""
utils.py – Ortak Yardımcı Fonksiyonlar
"""

import os
from datetime import timedelta


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def seconds_to_timedelta(sec: int) -> timedelta:
    return timedelta(seconds=int(sec))


def normalize_cell(cell_str: str) -> str:
    if not isinstance(cell_str, str):
        return ""
    s = cell_str.strip()
    if "-" in s:
        return s.split("-")[0].strip()
    return s
