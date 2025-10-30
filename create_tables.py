from server import app, db

with app.app_context():
    print("Forzando la creación de todas las tablas de la base de datos...")
    db.create_all()
    print("¡Tablas creadas con éxito!")
