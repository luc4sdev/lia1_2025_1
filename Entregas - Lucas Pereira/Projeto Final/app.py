from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from detector.roboflow_loader import baixar_modelo
from detector.contador import contar_veiculos
from agent.alerta import gerar_alerta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/processar", methods=["POST"])
def processar():
    # 1. Salvar vídeo enviado
    file = request.files["video"]
    filename = secure_filename(file.filename)
    video_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(video_path)

    # 2. Baixar modelo e processar
    model_path = baixar_modelo()
    resultado = contar_veiculos(model_path, video_path)
    alerta = gerar_alerta(resultado)

    # 3. Salvar na sessão
    session["resultado"] = resultado
    session["alerta"] = alerta

    return redirect(url_for("resultado"))

@app.route("/resultado")
def resultado():
    resultado = session.get("resultado", {})
    alerta = session.get("alerta", "Erro ao gerar alerta")

    return render_template("resultado.html", alerta=alerta, stats=resultado)

@app.route("/video")
def video():
    return send_from_directory("static", "video_saida_detectado.mp4")


if __name__ == "__main__":
    app.run(debug=True)

