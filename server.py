import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# --- Configuración ---
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    print("🚀 [MODO OFICINISTA] Iniciando y verificando tablas...")
    db.create_all()
    print("✅ [MODO OFICINISTA] Tablas listas.")

# --- Endpoint de la API ---
# Esta ruta ahora solo recibe datos y los guarda.
@app.route('/save_record', methods=['POST'])
def save_record():
    print("\n📝 ¡[MODO OFICINISTA] Recibida una nueva petición para guardar registro!")
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos en formato JSON'}), 400

        lote = data.get('lote')
        hilera = data.get('hilera')
        planta = data.get('planta')
        button_count = data.get('button_count')

        if None in [lote, hilera, planta, button_count]:
            return jsonify({'error': 'Faltan datos en la petición'}), 400

        print(f"   - Datos recibidos: Lote={lote}, Hilera={hilera}, Planta={planta}, Conteo={button_count}")
        
        print("   - Guardando registro en la base de datos...")
        new_record = FloralRecordDB(
            lote=lote,
            hilera=hilera,
            planta=planta,
            button_count=button_count
        )
        db.session.add(new_record)
        db.session.commit()
        print("   - ✅ Registro guardado con éxito en la base de datos.")
        
        return jsonify({'message': 'Registro guardado con éxito'}), 200

    except Exception as e:
        print(f"❌ Error durante la operación de guardado: {e}")
        db.session.rollback()
        return jsonify({'error': f'Error en el servidor: {e}'}), 500

# --- Punto de Entrada (Solo para pruebas locales) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
