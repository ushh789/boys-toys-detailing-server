import re
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GOOGLE_SHEETS_KEY = os.getenv("GOOGLE_SHEETS_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

app = Flask(__name__)
CORS(app,
     origins=["https://localhost:8080",
              "http://localhost:8080",
              "https://boystoys.com.ua",
              "http://boystoys.com.ua",
              "https://boystoys.online",
              "http://boystoys.online"])


def is_valid_ukrainian_phone(phone):
    regex = r'^(((\+?38)[-\s\(\.]?\d{3}[-\s\)\.]?)|([\.(]?0\d{2}[\.)]?))?[-\s\.]?\d{3}[-\s\.]?\d{2}[-\s\.]?\d{2}$'
    pattern = re.compile(regex)
    return bool(pattern.match(phone))


def send_to_telegram(name, phone):
    message = f"Новий запит:\nІм'я: {name}\nТелефон: {phone}"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.status_code == 200
    except Exception as e:
        (print("Помилка при відправці до Telegram:", e))
    return False


def format_price_list(data):
    price_list = []
    length = len(data)

    for i in range(1, length):
        if len(data[i]) < 5:
            row = {
                "category": data[i][0],
                "price": data[i][1],
                "typeOfService": data[i][2],
                "title": data[i][3]
            }
        else:
            row = {
                "category": data[i][0],
                "price": data[i][1],
                "typeOfService": data[i][2],
                "title": data[i][3],
                "description": data[i][4]
            }
        price_list.append(row)
    return price_list


@app.route("/status", methods=["GET"])
def example():
    return "API is working"


price_list_cache = {
    "data": None,
    "timestamp": 0
}
CACHE_TTL = 10 * 60


@app.route('/price_list', methods=['GET'])
def retrieve_price_list():
    current_time = time.time()

    if price_list_cache["data"] and (current_time - price_list_cache["timestamp"] < CACHE_TTL):
        return jsonify(price_list_cache["data"]), 200

    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Pricelist!A1:E80?key={GOOGLE_SHEETS_KEY}'

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except Exception as e:
        return jsonify({
            "error": "Не вдалося отримати прайс-лист",
            "details": str(e)
        }), 500

    sheet_data = response.json()
    if "values" not in sheet_data:
        return jsonify({"error": "Прайс-лист порожній"}), 404

    formatted_data = format_price_list(sheet_data["values"])

    price_list_cache["data"] = formatted_data
    price_list_cache["timestamp"] = current_time

    return jsonify(formatted_data), 200


@app.route("/send", methods=["POST"])
def handle_request():
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")
    if not name or not phone:
        return jsonify({"error": "Ім'я та телефон обов'язкові"}), 400
    if not is_valid_ukrainian_phone(phone):
        return jsonify(
            {"error": "Невірний формат телефонного номера. Повинно бути в українському форматі"}), 400
    if send_to_telegram(name, phone):
        return jsonify({"message": "Повідомлення відправлено"}), 200
    else:
        return jsonify({"error": "Помилка відправки до Telegram"}), 500
