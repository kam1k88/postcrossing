#!/usr/bin/env python3
"""
Добавление результата прогноза в файл
Запускайте после выполнения ноутбука на Kaggle
"""

import sys
from datetime import datetime


def add_forecast_result(forecast_date):
    """Добавляет результат прогноза в файл"""
    
    analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    result_file = "docs/forecast_results.txt"
    
    # Создаём строки для записи
    line1 = f"АНАЛИЗ ЗАВЕРШЁН (время анализа: {analysis_time})"
    line2 = f"Финальный прогноз достижения 88 млн: {forecast_date}"
    
    print("\n" + "="*70)
    print("📝 Сохранение результатов прогноза")
    print("="*70)
    
    # Записываем в файл
    try:
        with open(result_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{line1}\n")
            f.write(f"{line2}\n")
        
        print(f"\n✅ Результаты добавлены в {result_file}:")
        print(f"   {line1}")
        print(f"   {line2}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при записи в файл: {e}")
        return False


def main():
    """Основная функция"""
    
    if len(sys.argv) != 2:
        print("Использование: python add_forecast.py <дата_прогноза>")
        print("Пример: python add_forecast.py '2026-08-29 04:52:17'")
        sys.exit(1)
    
    forecast_date = sys.argv[1]
    
    # Проверяем формат даты (базовая проверка)
    if len(forecast_date) != 19 or forecast_date[4] != '-' or forecast_date[10] != ' ':
        print("⚠️  Предупреждение: дата должна быть в формате 'YYYY-MM-DD HH:MM:SS'")
    
    success = add_forecast_result(forecast_date)
    
    if success:
        print("\n✅ Готово! Не забудьте закоммитить изменения в git")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
