import os
from flask import Flask, request, jsonify
from ultralytics import YOLO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# --- Configuración ---
# Render nos dará esta URL para conectarnos a nuestra base de datos en la nube.
# Si no la encuentra, usa una base de datos local temporal llamada 'test.db'.
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///test.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Modelo de la Base de Datos ---
# Así es como se verá la tabla en nuestra base de datos en la nube.
class FloralRecordDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lote = db.Column(db.String(80), nullable=False)
    hilera = db.Column(db.String(80), nullable=False)
    planta = db.Column(db.String(80), nullable=False)
    button_count = db.Column(db.Integer, nullable=False)
    # ¡Podríamos añadir fecha, nombre de la imagen, etc. en el futuro!

# --- Carga del Modelo IA ---
# (Esto sigue igual, pero es importante que 'best.pt' esté en la carpeta)
try:
    model = YOLO('best.pt')
    print("✅ Modelo 'best.pt' cargado con éxito.")
except Exception as e:
    print(f"❌ Error crítico al cargar 'best.pt': {e}")
    # En un servidor real, esto debería detener el arranque.

# --- Endpoint de la API ---
@app.route('/upload', methods=['POST'])
def upload_file():
    print("\n📸 ¡Recibida una nueva petición desde la app!")
    
    if 'image' not in request.files:
        print("❌ Error: La petición no contenía una imagen.")
        return jsonify({'error': 'No se encontró una imagen'}), 400

    image_file = request.files['image']
    lote = request.form.get('lote', 'N/A')
    hilera = request.form.get('hilera', 'N/A')
    planta = request.form.get('planta', 'N/A')
    
    # Creamos una carpeta 'uploads' si no existe, para guardar la imagen temporalmente
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    image_path = os.path.join(uploads_dir, image_file.filename)
    image_file.save(image_path)

    try:
        # 1. Ejecutar el modelo de predicción
        print("   - Ejecutando el modelo de predicción...")
        results = model(image_path)
        detection_count = len(results[0].boxes)
        print(f"   - ✅ Predicción finalizada. Se encontraron {detection_count} detecciones.")
        
        # 2. Guardar el resultado en la Base de Datos
        print("   - Guardando registro en la base de datos...")
        new_record = FloralRecordDB(
            lote=lote,
            hilera=hilera,
            planta=planta,
            button_count=detection_count
        )
        db.session.add(new_record)
        db.session.commit()
        print("   - ✅ Registro guardado con éxito.")
        
        # 3. Construir y enviar la respuesta a la app
        response_data = {
            'lote': lote,
            'hilera': hilera,
            'planta': planta,
            'button_count': detection_count
        }
        return jsonify(response_data)

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"❌ Error de base de datos: {e}")
        return jsonify({'error': f'Error en el servidor al guardar en DB: {e}'}), 500
    except Exception as e:
        print(f"❌ Error durante la predicción: {e}")
        return jsonify({'error': f'Error en el servidor: {e}'}), 500
    finally:
        # 4. Borrar la imagen temporal
        if os.path.exists(image_path):
            os.remove(image_path)

# --- Punto de Entrada ---
# Esta parte es para que el servidor sepa qué hacer cuando se inicia.
if __name__ == '__main__':
    with app.app_context():
        print("🚀 Iniciando el servidor Flask...")
        # Esta línea crea la tabla en la base de datos si no existe.
        db.create_all()
        print("✅ Tablas de la base de datos verificadas/creadas.")
    
    # Render usará gunicorn, pero esto es útil para pruebas locales.
    # El host '0.0.0.0' es crucial para que sea visible en la red.
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
