#!/usr/bin/env python3
"""Скачивает TimeData.csv с HF и берёт его за эталон"""

import requests
import pandas as pd
from io import StringIO

url = "https://huggingface.co/datasets/kamjke/postcrossing-daily-growth/raw/main/TimeData.csv"

print("📥 Скачиваем TimeData.csv с Hugging Face...")
r = requests.get(url)
r.raise_for_status()

hf = pd.read_csv(StringIO(r.text))
print(f"✅ Строк на HF: {len(hf)}")
print(f"   Первая запись: {hf.iloc[0]['datetime']}")
print(f"   Последняя:     {hf.iloc[-1]['datetime']} = {hf.iloc[-1]['postcards_received']:,}")

# Сохраняем локально
hf.to_csv("docs/TimeData.csv", index=False)
print(f"\n✅ Сохранено в docs/TimeData.csv ({len(hf)} строк)")
