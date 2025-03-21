from flask import Flask, render_template, jsonify, send_from_directory
import os
import subprocess
from datetime import datetime
import pytz

app = Flask(__name__)
CSV_PATH = "/var/www/html/csv_reports/"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/ejecutar-horas', methods=['GET', 'POST'])
def ejecutar_horas():
    try:
        os.chdir("/home/flaskapp/horas")
        subprocess.run(["sudo", "-u", "flaskapp", "venv/bin/python", "horas-server.py"])
        return jsonify({"message": "Script ejecutado correctamente"})
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/descargar-csv/<yyyymm>', methods=['GET'])
def descargar_csv(yyyymm):
    archivo = f"{yyyymm[:4]}-{yyyymm[4:]}.csv"
    if os.path.exists(os.path.join(CSV_PATH, archivo)):
        return send_from_directory(CSV_PATH, archivo, as_attachment=True)
    return jsonify({"message": "Archivo no encontrado"}), 404

@app.route('/listar-archivos', methods=['GET'])
def listar_archivos():
    archivos = []
    try:
        if not os.path.exists(CSV_PATH):
            return jsonify({"error": "El directorio no existe"}), 500

        zona_horaria = pytz.timezone("America/Argentina/Buenos_Aires")  # UTC-3

        for archivo in sorted(os.listdir(CSV_PATH), reverse=True):
            ruta_completa = os.path.join(CSV_PATH, archivo)
            if os.path.isfile(ruta_completa):
                fecha_modificacion = os.path.getmtime(ruta_completa)
                fecha_legible = datetime.fromtimestamp(fecha_modificacion, pytz.utc).astimezone(zona_horaria).strftime('%Y-%m-%d %H:%M:%S')
                archivos.append({"nombre": archivo, "fecha": fecha_legible})

        return jsonify({"archivos": archivos})
    except Exception as e:
        return jsonify({"error": f"Error al listar archivos: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
