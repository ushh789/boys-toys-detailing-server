import re
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
CORS(app, origins=["http://localhost:8082"])

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

@app.route('/price_list', methods=['GET'])
def retrieve_price_list():
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Pricelist!A1:E80?key={GOOGLE_SHEETS_KEY}'
    response = requests.get(url)

    if response.status_code == 200:
        sheet_data = response.json()

        if "values" in sheet_data:
            data = sheet_data["values"]
            return jsonify(format_price_list(data)), 200
        else:
            return jsonify({
                "error": "Інформація про прайс-лист порожня"
            }), 404

    else:
        return jsonify({
            "error": "Не вдалось отримати інформацію про прайс-лист",
            "status_code": response.status_code,
            "details": response.text
        }), response.status_code


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
