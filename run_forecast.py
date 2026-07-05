#!/usr/bin/env python3
"""
Автоматический запуск ноутбука прогноза на Kaggle и сохранение результатов
"""

import os
import sys
import time
import re
from datetime import datetime

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
except ImportError:
    print("❌ Модуль kaggle не установлен. Установите: pip install kaggle")
    sys.exit(1)


def run_kaggle_notebook():
    """Запускает ноутбук на Kaggle и получает результаты"""
    
    print("🚀 Запуск прогноза на Kaggle...\n")
    
    # Инициализация Kaggle API
    api = KaggleApi()
    api.authenticate()
    
    # Информация о ноутбуке
    kernel_slug = "arkadymaximov/ctulhufagn2"
    
    print(f"📊 Ноутбук: {kernel_slug}")
    
    # Запуск ноутбука
    print("⏳ Запуск выполнения...")
    try:
        # Получаем статус ноутбука
        kernel_info = api.kernel_status(kernel_slug)
        
        # Пушим новую версию для выполнения
        api.kernels_push_cli(kernel_slug)
        
        print("✅ Ноутбук отправлен на выполнение")
        print("⏳ Ожидание завершения (это может занять несколько минут)...\n")
        
        # Ждём завершения
        max_wait = 600  # 10 минут
        wait_time = 0
        check_interval = 15
        
        while wait_time < max_wait:
            time.sleep(check_interval)
            wait_time += check_interval
            
            status = api.kernel_status(kernel_slug)
            print(f"⏱️  {wait_time}с - Статус: {status}")
            
            if status in ['complete', 'error', 'cancelled']:
                break
        
        if status == 'complete':
            print("\n✅ Ноутбук выполнен успешно!")
            return True
        elif status == 'error':
            print("\n❌ Ошибка при выполнении ноутбука")
            return False
        else:
            print(f"\n⚠️  Неожиданный статус: {status}")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка при работе с Kaggle API: {e}")
        return False


def extract_forecast_from_output(output_text):
    """Извлекает прогноз из вывода ноутбука"""
    
    # Ищем строку вида: "Финальный прогноз достижения 88 млн: 2026-08-29 04:52:17"
    pattern = r"Финальный прогноз достижения 88 млн:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"
    match = re.search(pattern, output_text)
    
    if match:
        return match.group(1)
    
    return None


def save_forecast_result(forecast_date):
    """Сохраняет результат прогноза в файл"""
    
    analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    result_file = "docs/forecast_results.txt"
    
    # Создаём строки для записи
    line1 = f"АНАЛИЗ ЗАВЕРШЁН (время анализа: {analysis_time})"
    line2 = f"Финальный прогноз достижения 88 млн: {forecast_date}"
    
    # Записываем в файл
    with open(result_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{line1}\n")
        f.write(f"{line2}\n")
    
    print(f"\n📝 Результаты сохранены в {result_file}")
    print(f"   {line1}")
    print(f"   {line2}")
    
    return result_file


def main():
    """Основная функция"""
    
    print("="*70)
    print("🔮 АВТОМАТИЧЕСКИЙ ПРОГНОЗ POSTCROSSING")
    print("="*70)
    print()
    
    # Проверяем наличие credentials для Kaggle
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_json):
        print("❌ Не найден файл ~/.kaggle/kaggle.json")
        print("📖 Инструкция:")
        print("   1. Зайдите на https://www.kaggle.com/settings")
        print("   2. Нажмите 'Create New Token'")
        print("   3. Сохраните kaggle.json в ~/.kaggle/")
        sys.exit(1)
    
    # Запускаем ноутбук на Kaggle
    success = run_kaggle_notebook()
    
    if not success:
        print("\n❌ Не удалось выполнить прогноз")
        sys.exit(1)
    
    # TODO: Получить вывод ноутбука и извлечь прогноз
    # Пока что используем mock данные
    print("\n⚠️  Примечание: Автоматическое извлечение результатов будет добавлено")
    print("   Пожалуйста, проверьте результаты вручную на Kaggle:")
    print(f"   https://www.kaggle.com/code/arkadymaximov/ctulhufagn2")
    
    # Пример: сохраняем результат (позже заменим на реальные данные)
    # forecast_date = "2026-08-29 04:52:17"
    # save_forecast_result(forecast_date)
    
    print("\n✅ Готово!")


if __name__ == '__main__':
    main()
