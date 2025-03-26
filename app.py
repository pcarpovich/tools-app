from flask import Flask, render_template, jsonify, send_from_directory, Response
import os
import subprocess
from datetime import datetime
import pytz

# Cargar variables desde .env
from dotenv import load_dotenv
load_dotenv()

# AirTable
from pyairtable import Api

# CSV
import csv
import io

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

@app.route('/clientes', methods=['GET'])
def obtener_clientes_airtable():
    try:
        ACCESS_TOKEN = os.environ.get("AIRTABLE_ACCESS_TOKEN")
        if not ACCESS_TOKEN:
            return jsonify({"error": "Token de acceso no configurado"}), 500

        BASE_ID = "appnenEA8D7juDwkq"
        TABLE_NAME = "tblPlC3tm78fXpXru"

        api = Api(ACCESS_TOKEN)
        table = api.table(BASE_ID, TABLE_NAME)

        records = table.all()

        all_keys = set()
        for record in records:
            all_keys.update(record['fields'].keys())

        all_keys = sorted(all_keys)
        data = []
        for record in records:
            fields = record['fields']
            row = {key: fields.get(key, "") for key in all_keys}
            data.append(row)

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clientes.csv', methods=['GET'])
def obtener_clientes_csv():
    try:
        ACCESS_TOKEN = os.environ.get("AIRTABLE_ACCESS_TOKEN")
        if not ACCESS_TOKEN:
            return jsonify({"error": "Token de acceso no configurado"}), 500

        BASE_ID = "appnenEA8D7juDwkq"
        TABLE_NAME = "tblPlC3tm78fXpXru"

        api = Api(ACCESS_TOKEN)
        table = api.table(BASE_ID, TABLE_NAME)

        records = table.all()

        all_keys = set()
        for record in records:
            all_keys.update(record['fields'].keys())

        all_keys = sorted(all_keys)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=all_keys)
        writer.writeheader()

        for record in records:
            fields = record['fields']
            row = {key: fields.get(key, "") for key in all_keys}
            writer.writerow(row)

        csv_content = output.getvalue()
        output.close()

        return Response(
            csv_content,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment; filename=clientes.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/servicios', methods=['GET'])
def generar_servicios_pdf():
    try:
        os.chdir("/home/flaskapp/horas")
        resultado = subprocess.run(
            ["sudo", "-u", "flaskapp", "venv/bin/python", "servicios.py"],
            capture_output=True,
            text=True
        )

        if resultado.returncode != 0:
            return jsonify({"error": "Error al generar el PDF", "detalle": resultado.stderr}), 500

        pdf_path = os.path.join(CSV_PATH, "servicios.pdf")
        if os.path.exists(pdf_path):
            return send_from_directory(CSV_PATH, "servicios.pdf", as_attachment=True)
        else:
            return jsonify({"error": "No se encontró el archivo generado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clientes_horas', methods=['GET'])
def generar_clientes_csv():
    try:
        os.chdir("/home/flaskapp/horas")
        resultado = subprocess.run(
            ["sudo", "-u", "flaskapp", "venv/bin/python", "clientes_fast.py"],
            capture_output=True,
            text=True
        )

        if resultado.returncode != 0:
            return jsonify({"error": "Error al generar el CSV", "detalle": resultado.stderr}), 500

        csv_path = os.path.join(CSV_PATH, "clientes_horas.csv")
        if os.path.exists(csv_path):
            return send_from_directory(CSV_PATH, "clientes_horas.csv", as_attachment=True)
        else:
            return jsonify({"error": "No se encontró el archivo generado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
