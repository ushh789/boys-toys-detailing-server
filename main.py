import re
from flask import Flask, request, jsonify
import configparser
import requests

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.cfg")
TELEGRAM_TOKEN = config["DEFAULT"]["TELEGRAM_TOKEN"]
CHAT_ID = config["DEFAULT"]["CHAT_ID"]


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

@ app.route("/send", methods=["POST"])
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
