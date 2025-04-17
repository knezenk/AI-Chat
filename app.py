from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import os
import requests
from pyngrok import ngrok, conf
from agente import agent, realizar_treinamento

# Load variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Configurações
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
NGROK = os.getenv("NGROK")

# Configurar ngrok
conf.get_default().auth_token = NGROK
ngrok_tunnel = ngrok.connect(5010)
print("🔗 URL pública gerada pelo ngrok:", ngrok_tunnel.public_url)

# Realiza treinamento ao iniciar o servidor
realizar_treinamento()

# Rotas
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
        resposta = agent(user_msg)  # Chamada ao agente
        return jsonify({"reply": resposta})
    except Exception as e:
        return jsonify({"reply": f"Erro: {str(e)}"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Rodar o servidor Flask
if __name__ == "__main__":
    app.run(port=5010)
