from flask import Flask, request
import sqlite3
 
app = Flask(__name__)
db_name = 'claves.db'  # Nombre del archivo de la base de datos
 
def init_db():
    """Crea la base de datos y la tabla usuarios si no existen."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
 
@app.route('/')
def inicio():
    """Ruta raíz: muestra mensaje de bienvenida."""
    return "Bienvenido al sistema de gestión de claves (Fase 1)"
 
@app.route('/registrar', methods=['POST'])
def registrar():
    """Registra un nuevo usuario con nombre y contraseña en texto plano."""
    nombre = request.form.get('nombre', '')
    password = request.form.get('password', '')
    if not nombre or not password:
        return "Faltan nombre o password", 400
 
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO usuarios (nombre, password) VALUES (?, ?)',
            (nombre, password)
        )
        conn.commit()
        conn.close()
        return "Usuario registrado exitosamente", 201
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return "El nombre de usuario ya existe", 409
 
@app.route('/login', methods=['POST'])
def login():
    """Verifica las credenciales del usuario."""
    nombre = request.form.get('nombre', '')
    password = request.form.get('password', '')
    if not nombre or not password:
        return "Faltan nombre o password", 400
 
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM usuarios WHERE nombre = ?', (nombre,))
    result = cursor.fetchone()
    conn.close()
 
    if result and result[0] == password:
        return "Inicio de sesión exitoso", 200
    else:
        return "Credenciales inválidas", 401
 
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5800)
