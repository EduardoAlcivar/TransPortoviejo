from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)

app.secret_key = 'mysecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'transporto'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

# USERS
@app.route('/users', methods=['GET', 'POST'])
def users():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']
        cur.execute("INSERT INTO users (nombre, email, telefono, fecha_nacimiento) VALUES (%s, %s, %s, %s)",
                    (nombre, email, telefono, fecha_nacimiento))
        mysql.connection.commit()
        flash('Usuario registrado exitosamente')
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
        cur.execute("UPDATE users SET nombre = %s, email = %s, telefono = %s, fecha_nacimiento = %s WHERE id = %s",
                    (nombre, email, telefono, fecha_nacimiento, id))
        mysql.connection.commit()
        flash('Usuario actualizado con éxito')
        return redirect(url_for('users'))
    cur.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cur.fetchone()
    cur.close()
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Usuario eliminado exitosamente')
    return redirect(url_for('users'))

# COOPERATIVES
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
        flash('Cooperativa registrada con éxito')
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
        cur.execute("UPDATE cooperatives SET nombre = %s, color = %s, ciudad = %s WHERE id = %s",
                    (nombre, color, ciudad, id))
        mysql.connection.commit()
        flash('Cooperativa actualizada exitosamente')
        return redirect(url_for('cooperatives'))
    cur.execute("SELECT * FROM cooperatives WHERE id = %s", (id,))
    cooperative = cur.fetchone()
    cur.close()
    return render_template('edit_cooperative.html', cooperative=cooperative)

@app.route('/delete_cooperative/<int:id>', methods=['POST'])
def delete_cooperative(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cooperatives WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Cooperativa eliminada exitosamente')
    return redirect(url_for('cooperatives'))

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
        cur.execute("""
            UPDATE routes SET cooperativa_id=%s, descripcion=%s, tarifa=%s, horario=%s WHERE id=%s
        """, (cooperativa_id, descripcion, tarifa, horario, id))
        mysql.connection.commit()
        flash('Ruta actualizada correctamente')
        return redirect(url_for('routes'))
    cur.execute("SELECT * FROM routes WHERE id=%s", (id,))
    ruta = cur.fetchone()
    cur.execute("SELECT id, nombre FROM cooperatives")
    cooperativas = cur.fetchall()
    return render_template('edit_route.html', ruta=ruta, cooperativas=cooperativas)


@app.route('/eliminar_ruta/<int:id>', methods=['POST'])
def delete_route(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM routes WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Ruta eliminada correctamente')
    return redirect(url_for('routes'))

# RECHARGES
@app.route('/recharges', methods=['GET', 'POST'])
def recharges():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        user_id = request.form['user_id']
        monto = request.form['monto']
        metodo_pago = request.form['metodo_pago']
        cur.execute("INSERT INTO recharges (user_id, monto, metodo_pago) VALUES (%s, %s, %s)",
                    (user_id, monto, metodo_pago))
        mysql.connection.commit()
        flash('Recarga registrada exitosamente.')
        return redirect(url_for('recharges'))
    cur.execute("""
        SELECT recharges.id, users.nombre, recharges.monto, recharges.metodo_pago, recharges.fecha
        FROM recharges
        JOIN users ON recharges.user_id = users.id
    """)
    recargas = cur.fetchall()
    cur.execute("SELECT id, nombre FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('recharges.html', recargas=recargas, users=users)

@app.route('/edit_recharge/<int:id>', methods=['GET', 'POST'])
def edit_recharge(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        user_id = request.form['user_id']
        monto = request.form['monto']
        metodo_pago = request.form['metodo_pago']
        cur.execute("UPDATE recharges SET user_id = %s, monto = %s, metodo_pago = %s WHERE id = %s",
                    (user_id, monto, metodo_pago, id))
        mysql.connection.commit()
        flash('Recarga actualizada exitosamente.')
        return redirect(url_for('recharges'))
    cur.execute("SELECT * FROM recharges WHERE id = %s", (id,))
    recarga = cur.fetchone()
    cur.execute("SELECT id, nombre FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('edit_recharge.html', recarga=recarga, users=users)

@app.route('/delete_recharge/<int:id>', methods=['POST'])
def delete_recharge(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM recharges WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Recarga eliminada exitosamente.')
    return redirect(url_for('recharges'))


@app.route('/conductores', methods=['GET', 'POST'])
def conductores():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        ruta_id = request.form['ruta_id']
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        estado_civil = request.form['estado_civil']
        genero = request.form['genero']

        cur.execute("""
            INSERT INTO conductores (ruta_id, nombre, fecha_nacimiento, telefono, estado_civil, genero)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (ruta_id, nombre, fecha_nacimiento, telefono, estado_civil, genero))
        mysql.connection.commit()
        flash('Conductor agregado con éxito.')

    cur.execute("SELECT * FROM conductores")
    conductores = cur.fetchall()

    cur.execute("SELECT id, descripcion FROM routes")
    rutas = cur.fetchall()

    cur.close()
    return render_template('conductores.html', conductores=conductores, rutas=rutas)


@app.route('/edit_conductor/<int:id>', methods=['GET', 'POST'])
def edit_conductor(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        ruta_id = request.form['ruta_id']
        nombre = request.form['nombre']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        estado_civil = request.form['estado_civil']
        genero = request.form['genero']

        cur.execute("""
            UPDATE conductores 
            SET ruta_id=%s, nombre=%s, fecha_nacimiento=%s, telefono=%s, estado_civil=%s, genero=%s
            WHERE id=%s
        """, (ruta_id, nombre, fecha_nacimiento, telefono, estado_civil, genero, id))
        mysql.connection.commit()
        cur.close()
        flash('Conductor actualizado correctamente.')
        return redirect(url_for('conductores'))

    cur.execute("SELECT * FROM conductores WHERE id = %s", (id,))
    conductor = cur.fetchone()

    cur.execute("SELECT id, descripcion FROM routes")
    rutas = cur.fetchall()

    cur.close()
    return render_template('edit_conductor.html', conductor=conductor, rutas=rutas)


@app.route('/delete_conductor/<int:id>', methods=['POST'])
def delete_conductor(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM conductores WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Conductor eliminado correctamente.')
    return redirect(url_for('conductores'))


if __name__ == '__main__':
    app.run(debug=True)