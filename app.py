from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
API_URL = os.getenv("API_URL")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("chat"))
        return render_template("login.html", error="Usuário ou senha incorretos.")
    return render_template("login.html")

@app.route("/chat")
def chat():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def send():
    if not session.get("logged_in"):
        return jsonify({"reply": "Não autorizado."}), 401

    user_msg = request.get_json().get("message")
    try:
        res = requests.post(API_URL, json={"msg": user_msg})
        data = res.json()
        return jsonify({"reply": data.get("resposta", "Sem resposta.")})
    except Exception as e:
        return jsonify({"reply": f"Erro ao comunicar com a API: {str(e)}"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)
