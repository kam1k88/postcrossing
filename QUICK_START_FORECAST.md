# 🚀 Быстрый старт: Сохранение прогноза

## Шаг 1: Запустите ноутбук на Kaggle

Откройте: https://www.kaggle.com/code/arkadymaximov/ctulhufagn2

Нажмите **"Run All"** и дождитесь завершения.

## Шаг 2: Скопируйте результат

Найдите в конце вывода строку типа:
```
Финальный прогноз достижения 88 млн: 2026-08-29 04:52:17
```

Скопируйте дату и время: `2026-08-29 04:52:17`

## Шаг 3: Сохраните результат

```bash
python add_forecast.py "2026-08-29 04:52:17"
```

## Шаг 4: Отправьте на GitHub

```bash
git add docs/forecast_results.txt
git commit -m "forecast: add new prediction"
git push
```

## Готово! ✅

Результат сохранён в `docs/forecast_results.txt` и доступен через GitHub Pages.

---

📖 Подробная инструкция: [FORECAST_GUIDE.md](FORECAST_GUIDE.md)
