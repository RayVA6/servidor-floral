    import os
    from flask import Flask, request, jsonify
    # from ultralytics import YOLO # <-- COMENTADO PARA LA PRUEBA
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.exc import SQLAlchemyError
    
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    class FloralRecordDB(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        lote = db.Column(db.String(80), nullable=False)
        hilera = db.Column(db.String(80), nullable=False)
        planta = db.Column(db.String(80), nullable=False)
        button_count = db.Column(db.Integer, nullable=False)
    
    # --- Carga del Modelo IA (Desactivada para la prueba) ---
    # model = None
    # try:
    #     print("Saltando la carga del modelo para la prueba.")
    # except Exception as e:
    #     pass
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        print("\n📸 ¡[MODO PRUEBA] Recibida una nueva petición desde la app!")
        
        if 'image' not in request.files:
            return jsonify({'error': 'No se encontró una imagen'}), 400
    
        lote = request.form.get('lote', 'N/A')
        hilera = request.form.get('hilera', 'N/A')
        planta = request.form.get('planta', 'N/A')
        
        try:
            # 1. Simular el modelo de predicción
            print("   - [PRUEBA] Simulando predicción. Devolviendo un valor fijo de 5.")
            detection_count = 5 # VALOR FIJO PARA LA PRUEBA
            
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
    
    if __name__ == '__main__':
        with app.app_context():
            print("🚀 [MODO PRUEBA] Iniciando el servidor Flask...")
            db.create_all()
            print("✅ Tablas de la base de datos verificadas/creadas.")
        
        app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
    
