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

    # --- Endpoint de la API (Modo Prueba) ---
    @app.route('/upload', methods=['POST'])
    def upload_file():
        print("\n📸 ¡[MODO PRUEBA] Recibida una nueva petición desde la app!")
        if 'image' not in request.files:
            return jsonify({'error': 'No se encontró una imagen'}), 400
        lote = request.form.get('lote', 'N/A')
        hilera = request.form.get('hilera', 'N/A')
        planta = request.form.get('planta', 'N/A')
        try:
            print("   - [PRUEBA] Simulando predicción. Devolviendo un valor fijo de 5.")
            detection_count = 5 # VALOR FIJO
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
            response_data = {
                'lote': lote,
                'hilera': hilera,
                'planta': planta,
                'button_count': detection_count
            }
            return jsonify(response_data)
        except Exception as e:
            print(f"❌ Error durante la operación: {e}")
            db.session.rollback()
            return jsonify({'error': f'Error en el servidor: {e}'}), 500

    # --- Punto de Entrada ---
    if __name__ == '__main__':
        with app.app_context():
            print("🚀 [MODO PRUEBA] Iniciando el servidor Flask...")
            db.create_all()
            print("✅ Tablas de la base de datos verificadas/creadas.")
        app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
    
