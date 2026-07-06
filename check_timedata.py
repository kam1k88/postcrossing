#!/usr/bin/env python3
"""Проверка TimeData.csv на дубли и тройники"""

import pandas as pd

df = pd.read_csv("docs/TimeData.csv")
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

print(f"Всего строк: {len(df)}")
print()

# 1. Точные дубликаты datetime
exact = df[df.duplicated(subset="datetime", keep=False)]
if len(exact):
    print(f"⚠️  Точные дубликаты datetime ({len(exact)} строк):")
    print(exact.to_string())
else:
    print("✅ Точных дубликатов datetime нет")
print()

# 2. Три и более записей в один день
df["date"] = df["datetime"].dt.date
day_counts = df.groupby("date").size()
triples = day_counts[day_counts >= 3]
if len(triples):
    print(f"⚠️  Дней с 3+ записями ({len(triples)} дней):")
    for date, count in triples.items():
        rows = df[df["date"] == date][["datetime", "postcards_received"]]
        print(f"\n  {date} — {count} записей:")
        print(rows.to_string(index=False))
else:
    print("✅ Дней с 3+ записями нет")
print()

# 3. Записи с интервалом менее 1 часа
df["diff_min"] = df["datetime"].diff().dt.total_seconds() / 60
close = df[df["diff_min"] < 60].copy()
close = close[close["diff_min"] > 0]  # убираем первую строку
if len(close):
    print(f"⚠️  Записи с интервалом < 1 часа ({len(close)} пар):")
    for idx, row in close.iterrows():
        prev = df.loc[idx - 1]
        print(f"\n  [{idx-1}] {prev['datetime']}  {prev['postcards_received']:,}")
        print(f"  [{idx}] {row['datetime']}  {row['postcards_received']:,}  ← Δ {row['diff_min']:.1f} мин")
else:
    print("✅ Записей с интервалом < 1 часа нет")
