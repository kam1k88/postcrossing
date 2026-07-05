#!/usr/bin/env python3
"""Verify that GitHub and Hugging Face datasets are in sync"""

import requests
import pandas as pd
from datetime import datetime

def check_sync():
    print("🔍 Проверка синхронизации датасетов...\n")
    
    # 1. Проверка локального файла
    print("📁 Локальный файл (GitHub):")
    try:
        local_df = pd.read_csv('docs/TimeData.csv')
        local_last_date = local_df['datetime'].iloc[-1]
        local_last_value = local_df['postcards_received'].iloc[-1]
        local_rows = len(local_df)
        print(f"   ✅ Строк: {local_rows}")
        print(f"   ✅ Последняя дата: {local_last_date}")
        print(f"   ✅ Последнее значение: {local_last_value:,}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    # 2. Проверка файла на Hugging Face
    print("\n☁️  Файл на Hugging Face:")
    try:
        hf_url = "https://huggingface.co/datasets/kamjke/postcrossing-daily-growth/raw/main/TimeData.csv"
        response = requests.get(hf_url)
        response.raise_for_status()
        
        # Сохраняем во временный файл и читаем
        with open('temp_hf.csv', 'wb') as f:
            f.write(response.content)
        
        hf_df = pd.read_csv('temp_hf.csv')
        hf_last_date = hf_df['datetime'].iloc[-1]
        hf_last_value = hf_df['postcards_received'].iloc[-1]
        hf_rows = len(hf_df)
        print(f"   ✅ Строк: {hf_rows}")
        print(f"   ✅ Последняя дата: {hf_last_date}")
        print(f"   ✅ Последнее значение: {hf_last_value:,}")
        
        import os
        os.remove('temp_hf.csv')
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    # 3. Сравнение
    print("\n🔄 Сравнение:")
    if local_rows == hf_rows:
        print(f"   ✅ Количество строк совпадает: {local_rows}")
    else:
        print(f"   ⚠️  Количество строк различается! Local: {local_rows}, HF: {hf_rows}")
        return False
    
    if local_last_date == hf_last_date:
        print(f"   ✅ Последняя дата совпадает: {local_last_date}")
    else:
        print(f"   ⚠️  Последняя дата различается! Local: {local_last_date}, HF: {hf_last_date}")
        return False
    
    if local_last_value == hf_last_value:
        print(f"   ✅ Последнее значение совпадает: {local_last_value:,}")
    else:
        print(f"   ⚠️  Последнее значение различается! Local: {local_last_value}, HF: {hf_last_value}")
        return False
    
    # 4. Проверка последнего коммита на HF
    print("\n📝 Последний коммит на Hugging Face:")
    try:
        api_url = "https://huggingface.co/api/datasets/kamjke/postcrossing-daily-growth/commits/main"
        commits = requests.get(api_url).json()
        last_commit = commits[0]
        commit_date = datetime.fromisoformat(last_commit['date'].replace('Z', '+00:00'))
        print(f"   ✅ Дата коммита: {commit_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   ✅ Сообщение: {last_commit['title']}")
    except Exception as e:
        print(f"   ⚠️  Не удалось получить информацию о коммитах: {e}")
    
    print("\n" + "="*50)
    print("✅ Датасеты полностью синхронизированы!")
    print("="*50)
    return True

if __name__ == '__main__':
    check_sync()
