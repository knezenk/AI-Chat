from gtts import gTTS
import tempfile
from flask import send_file
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import os
import requests
from pyngrok import ngrok, conf
from agente import agent, realizar_treinamento
from flask_cors import CORS  # Importação correta do CORS

# Load variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurações do CORS devem vir depois de instanciar o app
CORS(app)

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


@app.route("/audio", methods=["POST"])
def audio():
    if not session.get("logged_in"):
        return jsonify({"erro": "Não autorizado."}), 401

    user_msg = request.get_json().get("message")
    try:
        resposta = agent(user_msg)

        # Converte resposta em áudio
        tts = gTTS(text=resposta, lang='pt')
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio.name)

        print(f"Áudio gerado com sucesso: {temp_audio.name}")  # Adicionado para depuração

        # Retorna áudio
        return send_file(temp_audio.name, mimetype="audio/mpeg")

    except Exception as e:
        print("Erro ao gerar áudio:", str(e))  # Adicionado para depuração
        return jsonify({"erro": f"Erro ao gerar áudio: {str(e)}"}), 500



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Rodar o servidor Flask
if __name__ == "__main__":
    app.run(port=5010)
