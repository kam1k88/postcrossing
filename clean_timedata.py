#!/usr/bin/env python3
"""Удаляем только явный дубль 2026-06-15 06:41:23 (разница 1.2 мин)"""

import pandas as pd

df = pd.read_csv("docs/TimeData.csv")
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

print(f"Строк до: {len(df)}")

# Удаляем только конкретный дубль
mask = df["datetime"] == pd.Timestamp("2026-06-15 06:41:23")
print(f"\nУдаляем:")
print(df[mask][["datetime", "postcards_received"]].to_string(index=False))

df_clean = df[~mask].reset_index(drop=True)
print(f"\nСтрок после: {len(df_clean)}")

df_clean.to_csv("docs/TimeData.csv", index=False)
print("✅ Сохранено в docs/TimeData.csv")
