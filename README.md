# Telegram Notification Service

---

## Опис

Ця програма забезпечує веб-сервер на основі **Flask**, який обробляє HTTP-запити

---

# How to run

## Залежності
Переконайтеся, що у вас встановлені наступні пакети:
- Flask
- CORS
- Requests

### Встановлення залежностей
Виконайте в терміналі:

```bash
pip install Flask requests flask-cors
```
---
### Налаштування

Крок 1: Створіть config.cfg
Створіть файл config.cfg в кореневій папці проєкту зі наступним вмістом:

```cfg
[DEFAULT]
TELEGRAM_TOKEN = YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID = YOUR_CHAT_ID
GOOGLE_SHEETS_API_KEY = YOUR_GOOGLE_SHEETS_API_KEY
SPREADSHEET_ID = YOUR_SPREADSHEET_ID
```

### Запуск

Запустіть сервер:
```bash
python main.py
```
Сервер слухає запити на порті 8081.

# Приклади використання

## POST-запит до /send
URL: http://localhost:8081/send

### Тіло запиту:
```json
{
  "name": "Ім'я користувача",
  "phone": "+380XXXXXXXXX"
}
```

## GET-запит до /price_list
URL: http://localhost:8081/price_list

### Тіло запиту:
```json
{}
```

# Вимоги
- Python 3.x
- Flask
- CORS
- Requests

