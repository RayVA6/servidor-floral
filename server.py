import os
from flask import Flask, request, jsonify
from ultralytics import YOLO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# --- Configuración ---
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- ¡CAMBIO CLAVE! ---
# No cargamos el modelo al principio, lo dejamos como "None"
model = None

# Función para cargar el modelo solo cuando se necesite
def load_model():
    global model
    if model is None:
        try:
            print("🧠 Cargando el modelo 'best.pt' por primera vez...")
            model = YOLO('best.pt')
            print("✅ Modelo cargado con éxito.")
        except Exception as e:
            print(f"❌ Error crítico al cargar 'best.pt': {e}")
            model = None # Asegurarse de que sigue siendo None si falla

# --- Modelo de la Base de Datos ---
class FloralRecordDB(db.Model):
    __tablename__ = 'floral_records'
    id = db.Column(db.Integer, primary_key=True)
    lote = db.Column(db.String(80), nullable=False)
    hilera = db.Column(db.String(80), nullable=False)
    planta = db.Column(db.String(80), nullable=False)
    button_count = db.Column(db.Integer, nullable=False)

# --- Creación de Tablas ---
with app.app_context():
    print("🚀 Iniciando el contexto de la aplicación y verificando tablas...")
    db.create_all()
    print("✅ Tablas de la base de datos verificadas/creadas.")

# --- Endpoint de la API ---
@app.route('/upload', methods=['POST'])
def upload_file():
    # ¡Llamamos a la función para asegurarnos de que el modelo está cargado!
    load_model()
    
    print("\n📸 ¡Recibida una nueva petición desde la app!")
    if 'image' not in request.files:
        return jsonify({'error': 'No se encontró una imagen'}), 400
    
    # ... (El resto del código sigue igual)
    image_file = request.files['image']
    lote = request.form.get('lote', 'N/A')
    hilera = request.form.get('hilera', 'N/A')
    planta = request.form.get('planta', 'N/A')
    
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    image_path = os.path.join(uploads_dir, image_file.filename)
    image_file.save(image_path)
    
    try:
        print("   - Ejecutando el modelo de predicción...")
        if model:
            results = model(image_path)
            detection_count = len(results[0].boxes)
            print(f"   - ✅ Predicción finalizada. Se encontraron {detection_count} detecciones.")
        else:
            print("   - ⚠️ ADVERTENCIA: Modelo no cargado. Devolviendo un valor fijo de -1.")
            detection_count = -1
        
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
        
        response_data = { 'lote': lote, 'hilera': hilera, 'planta': planta, 'button_count': detection_count }
        return jsonify(response_data)
    
    except Exception as e:
        print(f"❌ Error durante la operación: {e}")
        db.session.rollback()
        return jsonify({'error': f'Error en el servidor: {e}'}), 500
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

# --- Punto de Entrada (Solo para pruebas locales) ---
if __name__ == '__main__':
    print("Iniciando servidor para pruebas locales...")
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
