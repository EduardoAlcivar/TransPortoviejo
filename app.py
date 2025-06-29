from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'transporto'

mysql = MySQL(app)

@app.route('/')
def inicio():
    return render_template('principal.html')


@app.route('/users', methods=['GET', 'POST'])
def users():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']
        contraseña = request.form['contraseña']

        if not (nombre and email and telefono and fecha_nacimiento and contraseña):
            flash('Por favor completa todos los campos')
            return redirect(url_for('users'))

        # Verificar email único
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Correo electrónico ya registrado')
            cur.close()
            return redirect(url_for('users'))

        hashed_password = generate_password_hash(contraseña)

        cur.execute("""INSERT INTO users (nombre, email, telefono, fecha_nacimiento, contraseña)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (nombre, email, telefono, fecha_nacimiento, hashed_password))
        mysql.connection.commit()
        flash('Usuario agregado correctamente')
        cur.close()
        return redirect(url_for('users'))

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('users.html', users=users)


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']

        cur.execute("""UPDATE users SET nombre=%s, email=%s, telefono=%s, fecha_nacimiento=%s WHERE id=%s""",
                    (nombre, email, telefono, fecha_nacimiento, id))
        mysql.connection.commit()
        flash('Usuario modificado correctamente')
        cur.close()
        return redirect(url_for('users'))

    cur.execute("SELECT * FROM users WHERE id=%s", (id,))
    user = cur.fetchone()
    cur.close()
    return render_template('edit_user.html', user=user)


@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    cur = mysql.connection.cursor()

    # Primero eliminar las recargas asociadas al usuario
    cur.execute("DELETE FROM recharges WHERE user_id = %s", (id,))

    # Luego eliminar el saldo asociado al usuario (si existe)
    cur.execute("DELETE FROM saldos WHERE user_id = %s", (id,))

    # Finalmente eliminar el usuario
    cur.execute("DELETE FROM users WHERE id = %s", (id,))

    mysql.connection.commit()
    cur.close()
    flash('Usuario eliminado correctamente, junto con sus recargas y saldo asociado.')
    return redirect(url_for('users'))

@app.route('/cooperatives', methods=['GET', 'POST'])
def cooperatives():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        color = request.form['color']
        ciudad = request.form['ciudad']

        cur.execute("INSERT INTO cooperatives (nombre, color, ciudad) VALUES (%s, %s, %s)",
                    (nombre, color, ciudad))
        mysql.connection.commit()
        flash('Cooperativa registrada correctamente')
        cur.close()
        return redirect(url_for('cooperatives'))

    cur.execute("SELECT * FROM cooperatives")
    cooperatives = cur.fetchall()
    cur.close()
    return render_template('cooperatives.html', cooperatives=cooperatives)

@app.route('/edit_cooperative/<int:id>', methods=['GET', 'POST'])
def edit_cooperative(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        color = request.form['color']
        ciudad = request.form['ciudad']

        cur.execute("UPDATE cooperatives SET nombre=%s, color=%s, ciudad=%s WHERE id=%s",
                    (nombre, color, ciudad, id))
        mysql.connection.commit()
        flash('Cooperativa editada correctamente')
        cur.close()
        return redirect(url_for('cooperatives'))

    cur.execute("SELECT * FROM cooperatives WHERE id=%s", (id,))
    cooperative = cur.fetchone()
    cur.close()
    return render_template('edit_cooperative.html', cooperative=cooperative)

@app.route('/delete_cooperative/<int:id>', methods=['POST'])
def delete_cooperative(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cooperatives WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Cooperativa eliminada correctamente')
    return redirect(url_for('cooperatives'))

# -------- RUTAS --------
@app.route('/routes', methods=['GET', 'POST'])
def routes():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        cooperativa_id = request.form['cooperativa_id']
        descripcion = request.form['descripcion']
        tarifa = request.form['tarifa']
        horario = request.form['horario']

        cur.execute("INSERT INTO routes (cooperativa_id, descripcion, tarifa, horario) VALUES (%s, %s, %s, %s)",
                    (cooperativa_id, descripcion, tarifa, horario))
        mysql.connection.commit()
        flash('Ruta agregada correctamente')
        cur.close()
        return redirect(url_for('routes'))

    cur.execute("SELECT id, nombre FROM cooperatives")
    cooperativas = cur.fetchall()

    cur.execute("""
        SELECT routes.id, cooperatives.nombre, routes.descripcion, routes.tarifa, routes.horario
        FROM routes
        JOIN cooperatives ON routes.cooperativa_id = cooperatives.id
    """)
    rutas = cur.fetchall()
    cur.close()
    return render_template('routes.html', cooperativas=cooperativas, rutas=rutas)

@app.route('/edit_route/<int:id>', methods=['GET', 'POST'])
def edit_route(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        cooperativa_id = request.form['cooperativa_id']
        descripcion = request.form['descripcion']
        tarifa = request.form['tarifa']
        horario = request.form['horario']

        cur.execute("""UPDATE routes SET cooperativa_id=%s, descripcion=%s, tarifa=%s, horario=%s WHERE id=%s""",
                    (cooperativa_id, descripcion, tarifa, horario, id))
        mysql.connection.commit()
        flash('Ruta actualizada correctamente')
        cur.close()
        return redirect(url_for('routes'))

    cur.execute("SELECT * FROM routes WHERE id=%s", (id,))
    ruta = cur.fetchone()

    cur.execute("SELECT id, nombre FROM cooperatives")
    cooperativas = cur.fetchall()
    cur.close()
    return render_template('edit_route.html', ruta=ruta, cooperativas=cooperativas)

@app.route('/delete_route/<int:id>', methods=['POST'])
def delete_route(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM routes WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Ruta eliminada exitosamente')
    return redirect(url_for('routes'))

@app.route('/recharges', methods=['GET', 'POST'])
def recharges():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        monto = float(request.form['monto'])
        metodo_pago = request.form['metodo_pago']

        # Registrar la recarga
        cur.execute("""
            INSERT INTO recharges (user_id, monto, metodo_pago)
            VALUES (%s, %s, %s)
        """, (user_id, monto, metodo_pago))

        # Verificar si el usuario ya tiene un registro de saldo
        cur.execute("SELECT saldo FROM saldos WHERE user_id = %s", (user_id,))
        resultado = cur.fetchone()

        if resultado:
            # Actualizar saldo existente
            cur.execute("""
                UPDATE saldos
                SET saldo = saldo + %s
                WHERE user_id = %s
            """, (monto, user_id))
        else:
            # Insertar nuevo saldo
            cur.execute("""
                INSERT INTO saldos (user_id, saldo)
                VALUES (%s, %s)
            """, (user_id, monto))

        mysql.connection.commit()
        cur.close()
        flash('Recarga registrada correctamente')
        return redirect(url_for('recharges'))

    # Mostrar todas las recargas con nombres de usuario
    cur.execute("""
        SELECT recharges.id, users.nombre, recharges.monto, recharges.metodo_pago, recharges.fecha
        FROM recharges
        JOIN users ON recharges.user_id = users.id
    """)
    recargas = cur.fetchall()

    # Lista de usuarios para formulario
    cur.execute("SELECT id, nombre FROM users")
    users = cur.fetchall()

    cur.close()
    return render_template('recharges.html', recargas=recargas, users=users)


@app.route('/edit_recharge/<int:id>', methods=['GET', 'POST'])
def edit_recharge(id):
    cur = mysql.connection.cursor()

    # Obtener datos originales
    cur.execute("SELECT user_id, monto FROM recharges WHERE id = %s", (id,))
    original = cur.fetchone()
    if not original:
        flash('Recarga no encontrada.')
        return redirect(url_for('recharges'))

    user_id_original, monto_original = original

    if request.method == 'POST':
        user_id_nuevo = int(request.form['user_id'])
        monto_nuevo = float(request.form['monto'])
        metodo_pago = request.form['metodo_pago']

        diferencia = monto_nuevo - float(monto_original)

        # Actualizar recarga
        cur.execute("""
            UPDATE recharges
            SET user_id = %s, monto = %s, metodo_pago = %s
            WHERE id = %s
        """, (user_id_nuevo, monto_nuevo, metodo_pago, id))

        if user_id_nuevo == user_id_original:
            # Solo actualizar saldo del mismo usuario
            cur.execute("""
                UPDATE saldos
                SET saldo = saldo + %s
                WHERE user_id = %s
            """, (diferencia, user_id_nuevo))
        else:
            # Ajustar saldo usuario anterior
            cur.execute("""
                UPDATE saldos
                SET saldo = saldo - %s
                WHERE user_id = %s
            """, (monto_original, user_id_original))

            # Ajustar saldo usuario nuevo (insertar si no existe)
            cur.execute("SELECT saldo FROM saldos WHERE user_id = %s", (user_id_nuevo,))
            existe = cur.fetchone()

            if existe:
                cur.execute("""
                    UPDATE saldos
                    SET saldo = saldo + %s
                    WHERE user_id = %s
                """, (monto_nuevo, user_id_nuevo))
            else:
                cur.execute("""
                    INSERT INTO saldos (user_id, saldo)
                    VALUES (%s, %s)
                """, (user_id_nuevo, monto_nuevo))

        mysql.connection.commit()
        cur.close()
        flash('Recarga modificada correctamente.')
        return redirect(url_for('recharges'))

    # Obtener datos para formulario
    cur.execute("SELECT * FROM recharges WHERE id = %s", (id,))
    recarga = cur.fetchone()
    cur.execute("SELECT id, nombre FROM users")
    users = cur.fetchall()
    cur.close()

    return render_template('edit_recharge.html', recarga=recarga, users=users)


@app.route('/delete_recharge/<int:id>', methods=['POST'])
def delete_recharge(id):
    cur = mysql.connection.cursor()

    # Obtener recarga antes de borrar para ajustar saldo
    cur.execute("SELECT user_id, monto FROM recharges WHERE id = %s", (id,))
    recarga = cur.fetchone()
    if not recarga:
        flash('Recarga no encontrada.')
        return redirect(url_for('recharges'))

    user_id, monto = recarga

    # Eliminar recarga
    cur.execute("DELETE FROM recharges WHERE id = %s", (id,))

    # Restar monto del saldo del usuario
    cur.execute("""
        UPDATE saldos
        SET saldo = saldo - %s
        WHERE user_id = %s
    """, (monto, user_id))

    mysql.connection.commit()
    cur.close()
    flash('Recarga eliminada correctamente')
    return redirect(url_for('recharges'))

@app.route('/conductores', methods=['GET', 'POST'])
def conductores():
    cur = mysql.connection.cursor()
      
    cur.execute("SELECT id, descripcion FROM routes")
    rutas = cur.fetchall()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        estado_civil = request.form['estado_civil']
        genero = request.form['genero']
        ruta_id = request.form['ruta_id']

        cur.execute("""
            INSERT INTO drivers (nombre, fecha_nacimiento, telefono, estado_civil, genero, ruta_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, fecha_nacimiento, telefono, estado_civil, genero, ruta_id))
        mysql.connection.commit()
        flash('Conductor agregado correctamente')
        cur.close()
        return redirect(url_for('conductores'))

    # Obtener conductores con descripción de ruta
    cur.execute("""
        SELECT drivers.id, routes.descripcion, drivers.nombre, drivers.fecha_nacimiento, drivers.telefono, drivers.estado_civil, drivers.genero
        FROM drivers
        LEFT JOIN routes ON drivers.ruta_id = routes.id
    """)
    drivers = cur.fetchall()
    cur.close()
    
    return render_template('conductores.html', drivers=drivers, rutas=rutas)


@app.route('/editar_conductor/<int:id>', methods=['GET', 'POST'])
def editar_conductor(id):
    cur = mysql.connection.cursor()
    
   
    cur.execute("SELECT id, descripcion FROM routes")
    rutas = cur.fetchall()

    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        estado_civil = request.form['estado_civil']
        genero = request.form['genero']
        ruta_id = request.form['ruta_id']

        cur.execute("""
            UPDATE drivers
            SET nombre=%s, fecha_nacimiento=%s, telefono=%s, estado_civil=%s, genero=%s, ruta_id=%s
            WHERE id=%s
        """, (nombre, fecha_nacimiento, telefono, estado_civil, genero, ruta_id, id))
        mysql.connection.commit()
        flash('Conductor actualizado correctamente')
        cur.close()
        return redirect(url_for('conductores'))
 
    cur.execute("SELECT id, nombre, fecha_nacimiento, telefono, estado_civil, genero, ruta_id FROM drivers WHERE id=%s", (id,))
    driver = cur.fetchone()
    cur.close()
    
    if not driver:
        flash('Conductor no encontrado')
        return redirect(url_for('conductores'))
    
    return render_template('edit_conductor.html', driver=driver, rutas=rutas)


@app.route('/eliminar_conductor/<int:id>', methods=['POST'])
def eliminar_conductor(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM drivers WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Conductor eliminado correctamente')
    return redirect(url_for('conductores'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']
        contraseña = request.form['contraseña']

        if not (nombre and email and telefono and fecha_nacimiento and contraseña):
            flash('Por favor, completa todos los campos.')
            return redirect(url_for('registro'))

        hashed_password = generate_password_hash(contraseña)

        try:
            conn = mysql.connection
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('El correo electrónico ya está registrado.')
                cursor.close()
                return redirect(url_for('registro'))

            cursor.execute("""
                INSERT INTO users (nombre, email, telefono, fecha_nacimiento, contraseña) 
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, email, telefono, fecha_nacimiento, hashed_password))

            conn.commit()
            cursor.close()

            flash('Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect(url_for('login'))

        except Exception as err:
            flash(f'Error en la base de datos: {err}')
            return redirect(url_for('registro'))

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, nombre, email, contraseña FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], contraseña):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash('Has iniciado sesión correctamente')
            return redirect(url_for('menu'))  
        else:
            flash('Usuario o contraseña incorrectos')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('Sesión cerrada')
    return redirect(url_for('principal'))


@app.route('/menu')
def menu():
    if 'user_id' not in session:
        flash('Inicia sesión primero')
        return redirect(url_for('login'))
    return render_template('menu.html', user_name=session['user_name'])


@app.route('/informacion_personal')
def informacion_personal():
    if 'user_id' not in session:
        flash('Inicia sesión primero')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombre, fecha_nacimiento, telefono, email FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if user is None:
        flash('Usuario no encontrado')
        return redirect(url_for('menu'))

    user_data = {
        'nombre': user[0],
        'fecha_nacimiento': user[1],
        'telefono': user[2],
        'email': user[3]
    }

    return render_template('informacion_personal.html', user=user_data)


@app.route('/saldo')
def saldo():
    if 'user_id' not in session:
        flash('Inicia sesión primero')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Obtener el saldo desde la tabla saldos
    cur.execute("SELECT saldo FROM saldos WHERE user_id = %s", (user_id,))
    resultado = cur.fetchone()
    saldo_actual = resultado[0] if resultado else 0

    # Obtener historial de recargas para ese usuario
    cur.execute("""
        SELECT fecha, monto, metodo_pago 
        FROM recharges 
        WHERE user_id = %s 
        ORDER BY fecha DESC
    """, (user_id,))
    recargas_data = cur.fetchall()

    # Formatear recargas como lista de dicts para plantilla
    recargas = [{
        'fecha': r[0].strftime('%Y-%m-%d %H:%M:%S') if hasattr(r[0], 'strftime') else r[0],
        'monto': r[1],
        'metodo_pago': r[2]
    } for r in recargas_data]

    cur.close()
    return render_template('saldo.html', saldo=saldo_actual, recargas=recargas)


@app.route('/', methods=['GET', 'POST'])
def principal():
    if request.method == 'POST':
        opcion = request.form.get('opcion')
        if opcion == 'cliente':
            return redirect(url_for('login'))
        elif opcion == 'admin':
            return redirect(url_for('index'))
    return '''
    <form method="post">
        <button type="submit" name="opcion" value="cliente">Cliente</button>
        <button type="submit" name="opcion" value="admin">Administrador</button>
    </form>
    '''

@app.route('/login')
def n_login():
    return render_template('login.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route("/informe", methods=["GET", "POST"])
def informe():
    datos = None
    tipo = None
    fecha_inicio = None
    fecha_fin = None

    if request.method == "POST":
        tipo = request.form["tipo_informe"]
        fecha_inicio = request.form["fecha_inicio"]
        fecha_fin = request.form["fecha_fin"]

        cursor = mysql.connection.cursor()
        condicion_fecha = ""
        parametros = []

        # Para usuarios y conductores, no aplicar filtro de fecha (o solo si tienes un campo registro)
        if tipo in ["recargas"]:
            # Para recargas solo aplicar filtro si ambas fechas existen
            if fecha_inicio and fecha_fin:
                condicion_fecha = " WHERE fecha BETWEEN %s AND %s "
                parametros = [fecha_inicio, fecha_fin]

        # Consultas según tipo
        if tipo == "usuarios":
            consulta = """
                SELECT id, nombre, email, telefono, fecha_nacimiento
                FROM users
                ORDER BY id ASC
            """
            parametros = []  # Sin filtro de fecha

        elif tipo == "conductores":
            consulta = """
                SELECT id, nombre, fecha_nacimiento, telefono, estado_civil, genero
                FROM drivers
                ORDER BY id ASC
            """
            parametros = []  # Sin filtro de fecha

        elif tipo == "recargas":
            consulta = f"""
                SELECT r.id, u.nombre, r.monto, r.metodo_pago, r.fecha
                FROM recharges r
                JOIN users u ON r.user_id = u.id
                {condicion_fecha}
                ORDER BY r.id ASC
            """

        elif tipo == "rutas":
            consulta = """
                SELECT id, descripcion, tarifa, horario
                FROM routes
                ORDER BY id ASC
            """
            parametros = []

        elif tipo == "cooperativas":
            consulta = """
                SELECT id, nombre, color, ciudad
                FROM cooperatives
                ORDER BY nombre ASC
            """
            parametros = []

        else:
            consulta = ""
            parametros = []

        if consulta:
            cursor.execute(consulta, parametros)
            datos = cursor.fetchall()
            cursor.close()

    return render_template(
        "informes.html",
        datos=datos,
        tipo=tipo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )




if __name__ == '__main__':
    app.run(debug=True)
