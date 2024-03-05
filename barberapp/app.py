from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = '9acd50534022ad7e189470a9a9c53ec1'

# Configuración de la base de datos
app.config['DATABASE'] = 'barbershop.db'

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# Ruta para crear la base de datos y las tablas si no existen
@app.route('/init_db')
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            fecha DATE NOT NULL,
            monto REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

    flash('Base de datos inicializada', 'success')
    return redirect(url_for('index'))

# Validación de entrada para el formulario de registro
def validar_entrada(servicio, fecha, monto):
    if not servicio:
        return 'El tipo de servicio es obligatorio.'
    if not fecha:
        return 'La fecha es obligatoria.'
    
    try:
        monto = float(monto)
        if monto <= 0:
            return 'El monto debe ser mayor que cero.'
    except ValueError:
        return 'El monto debe ser un número válido.'
    
    return None

@app.route('/')
def index():
    # Renderiza la plantilla 'index.html'
    return render_template('index.html')

@app.route('/registrar_servicio', methods=['POST'])
def registrar_servicio():
    servicio = request.form['servicio']
    fecha = request.form['fecha']
    monto = request.form['monto']

    error = validar_entrada(servicio, fecha, monto)
    if error:
        flash(error, 'error')
    else:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO servicios (tipo, fecha, monto) VALUES (?, ?, ?)', (servicio, fecha, monto))
        conn.commit()
        conn.close()

        flash('Servicio registrado exitosamente', 'success')

    return redirect(url_for('index'))

# Función para calcular el total de servicios por día
def calcular_total_dia():
    fecha_actual = datetime.now().date()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(monto) FROM servicios WHERE fecha = ?', (fecha_actual,))
    total_dia = cursor.fetchone()[0]
    conn.close()
    return total_dia

# Función para calcular el total de servicios por mes
def calcular_total_mes():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT strftime("%Y-%m", fecha) AS mes, SUM(monto) FROM servicios GROUP BY mes')
    resultados = cursor.fetchall()
    conn.close()
    
    # Extraer solo los totales (segundo elemento de cada tupla)
    totales_mes = [total for mes, total in resultados]
    
    return totales_mes



@app.route('/sumar_servicios_por_mes', methods=['GET', 'POST'])
def sumar_servicios_por_mes():
    if request.method == 'POST':
        mes_seleccionado = request.form['mes']
    else:
        mes_seleccionado = request.args.get('mes', '01')  # Valor predeterminado para enero
    
    # Lógica para calcular la suma de servicios para el mes seleccionado
    conn = connect_db()
    cursor = conn.cursor()
    
    # Consulta SQL para calcular la suma de servicios por mes
    cursor.execute('''
        SELECT SUM(monto) FROM servicios
        WHERE strftime("%Y-%m", fecha) = ?
    ''', (f'2023-{mes_seleccionado}',))
    
    total_mes = cursor.fetchone()[0] or 0  # Si no hay resultados, establece el total en 0
    
    conn.close()
    
    # Renderiza la plantilla 'suma_mes.html' para mostrar el resultado
    return render_template('suma_mes.html', mes=mes_seleccionado, total_mes=total_mes)

@app.route('/ver_servicios', methods=['GET', 'POST'])
def ver_servicios():
    total_mes = calcular_total_mes()  # Calcular el total de servicios por mes

    if request.method == 'POST':
        fecha = request.form['fecha']
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM servicios WHERE fecha = ?', (fecha,))
        servicios = cursor.fetchall()
        conn.close()
        return render_template('index.html', servicios=servicios, total_mes=total_mes)
    else:
        # Si no se ha enviado el formulario, simplemente renderiza la página de inicio.
        return render_template('index.html', total_mes=total_mes)

# Resto del código...

@app.route('/sumar_servicios_dia')
def sumar_servicios_dia():
    total_dia = calcular_total_dia()
    return jsonify({"total_dia": total_dia})

@app.route('/sumar_servicios_mes')
def sumar_servicios_mes():
    total_mes = calcular_total_mes()  # Cambio de nombre de la función
    return jsonify({"total_mes": total_mes})

# En tu archivo app.py

# Lista en memoria para almacenar los registros de clientes mensuales
clientes_mensuales = []

@app.route('/registrar_cliente_mensual', methods=['GET', 'POST'])
def registrar_cliente_mensual():
    if request.method == 'POST':
        nombre = request.form['nombre']
        mes_pago = request.form['mes_pago']
        monto = request.form['monto']

        # Validación y lógica para registrar al cliente mensual
        # Esto puede incluir la inserción de datos en la lista clientes_mensuales

        # Agregar el cliente mensual a la lista
        clientes_mensuales.append((nombre, mes_pago,monto))

        flash('Cliente mensual registrado exitosamente', 'success')

    # Obtener la lista de clientes mensuales para mostrar en la tabla
    clientes = clientes_mensuales

    return render_template('registro_cliente_mensual.html', clientes=clientes)

# Otras rutas y lógica de la aplicación Flask aquí...




if __name__ == '__main__':
    app.run(debug=True)
