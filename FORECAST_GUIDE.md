# 🔮 Руководство по прогнозированию

## О прогнозе

Ноутбук [CTULHUFAGN2](https://www.kaggle.com/code/arkadymaximov/ctulhufagn2) на Kaggle выполняет прогноз достижения 88 миллионов открыток на Postcrossing.

## Как запустить прогноз

### 1. Запуск на Kaggle (вручную)

1. Откройте ноутбук: https://www.kaggle.com/code/arkadymaximov/ctulhufagn2
2. Нажмите кнопку **"Run All"** или **"Run"**
3. Дождитесь завершения выполнения (обычно 2-5 минут)
4. Найдите в выводе строку: `Финальный прогноз достижения 88 млн: YYYY-MM-DD HH:MM:SS`

### 2. Сохранение результата

После получения прогноза, сохраните его локально:

```bash
# Формат: python add_forecast.py "YYYY-MM-DD HH:MM:SS"
python add_forecast.py "2026-08-29 04:52:17"
```

Скрипт добавит две строки в файл `docs/forecast_results.txt`:
```
АНАЛИЗ ЗАВЕРШЁН (время анализа: 2026-07-05 19:55:54)
Финальный прогноз достижения 88 млн: 2026-08-29 04:52:17
```

### 3. Коммит изменений

```bash
git add docs/forecast_results.txt
git commit -m "forecast: add prediction for 88M postcards"
git push
```

## Автоматизация (будущее)

Для полной автоматизации потребуется:

1. **Вариант 1: Kaggle API**
   - Настроить Kaggle API credentials
   - Использовать `run_forecast.py` для автоматического запуска
   - Требуется Kaggle API token

2. **Вариант 2: Kaggle Notebook Scheduling**
   - Настроить расписание выполнения в самом ноутбуке на Kaggle
   - Добавить код в конец ноутбука для автоматической загрузки результатов

3. **Вариант 3: GitHub Actions + Kaggle**
   - Добавить Kaggle credentials в GitHub Secrets
   - Создать workflow для периодического запуска

## Формат вывода

### Текущий формат:
```
АНАЛИЗ ЗАВЕРШЁН (время анализа: YYYY-MM-DD HH:MM:SS)
Финальный прогноз достижения 88 млн: YYYY-MM-DD HH:MM:SS
```

### Идеальный формат (будущий):
```
Анализ завершен (время анализа: YYYY-MM-DD HH:MM:SS) : прогноз YYYY-MM-DD HH:MM:SS
```

## История результатов

Все результаты прогнозов сохраняются в файле:
- 📄 `docs/forecast_results.txt`
- 🌐 Доступен через GitHub Pages

## Скрипты

- **`add_forecast.py`** - добавить результат прогноза в файл
- **`run_forecast.py`** - запустить ноутбук через Kaggle API (требует настройки)

## Пример использования

```bash
# 1. Запустите ноутбук на Kaggle
# 2. Скопируйте дату прогноза из вывода
# 3. Добавьте результат:
python add_forecast.py "2026-08-29 04:52:17"

# 4. Закоммитьте:
git add docs/forecast_results.txt
git commit -m "forecast: update prediction"
git push
```

## Интеграция с Hugging Face

Файл `forecast_results.txt` можно также синхронизировать с Hugging Face датасетом:

```python
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj='docs/forecast_results.txt',
    path_in_repo='forecast_results.txt',
    repo_id='kamjke/postcrossing-daily-growth',
    repo_type='dataset',
    token=YOUR_HF_TOKEN
)
```

---

*Дата создания: 2026-07-05*
