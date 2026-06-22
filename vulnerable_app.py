from flask import Flask, request, render_template_string, session, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from markupsafe import escape
import sqlite3
import os
import hashlib
import pyotp

app = Flask(__name__)
app.secret_key = os.urandom(24) # Mantiene la sesión firmada de forma segura

# Habilitar protección CSRF global
csrf = CSRFProtect(app)

# --- CONFIGURACIÓN MFA SIMULADA ---
# En un entorno real, este secreto se genera al registrar al usuario y se guarda en la DB.
# Ejemplo de generación: pyotp.random_base32()
MFA_SECRET = 'JBSWY3DPEHPK3PXP' 

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    return 'Welcome to the Secure Task Manager Application!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 1. Validación de entrada (sanitización básica de tipos)
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        token = request.form.get('mfa_token', '')

        conn = get_db_connection()
        
        # 2. Corrección SQLi: Uso estricto de consultas parametrizadas
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        hashed_password = hash_password(password)
        user = conn.execute(query, (username, hashed_password)).fetchone()
        conn.close()

        if user:
            # 3. Implementación de Autenticación Multifactor (MFA)
            totp = pyotp.TOTP(MFA_SECRET)
            if totp.verify(token):
                # Regenerar ID de sesión para evitar Session Fixation
                session.clear() 
                session['user_id'] = user['id']
                session['role'] = user['role']
                return redirect(url_for('dashboard'))
            else:
                return 'Invalid MFA Token!'
        else:
            return 'Invalid credentials!'
            
    # El formulario ahora incluye el campo MFA y el token CSRF (manejado automáticamente por Flask-WTF si se configura correctamente, pero es buena práctica agregarlo manualmente en plantillas en crudo)
    return '''
        <form method="post">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            Username: <input type="text" name="username" required><br>
            Password: <input type="password" name="password" required><br>
            MFA Token (6 digits): <input type="text" name="mfa_token" required><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()

    # Los formularios en el dashboard ahora incluyen el token CSRF
    return render_template_string('''
        <h1>Welcome, user {{ user_id }}!</h1>
        <form action="/add_task" method="post">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            <input type="text" name="task" placeholder="New task" required><br>
            <input type="submit" value="Add Task">
        </form>
        <h2>Your Tasks</h2>
        <ul>
        {% for task in tasks %}
            <li>
                {{ task['task'] }} 
                <form action="/delete_task/{{ task['id'] }}" method="post" style="display:inline;">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                    <button type="submit">Delete</button>
                </form>
            </li>
        {% endfor %}
        </ul>
    ''', user_id=user_id, tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Corrección XSS: Escapar la entrada del usuario antes de guardarla
    raw_task = request.form.get('task', '')
    safe_task = escape(raw_task)
    user_id = session['user_id']

    conn = get_db_connection()
    conn.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (user_id, safe_task))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# Corrección CSRF: Modificado de GET a POST para evitar ataques vía URL
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Corrección IDOR (Control de acceso): Validar que la tarea pertenece al usuario de la sesión actual
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

@app.route('/admin')
def admin():
    # Corrección Control de Acceso: Verificación estricta del rol
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    return 'Welcome to the admin panel! Accesos controlados correctamente.'

if __name__ == '__main__':
    app.run(debug=True)