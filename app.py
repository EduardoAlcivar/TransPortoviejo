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
        flash('User registered successfully')
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
        flash('User updated successfully')
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
    flash('User deleted successfully')
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
        flash('Cooperative registered successfully')
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
        flash('Cooperative updated successfully')
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
    flash('Cooperative deleted successfully')
    return redirect(url_for('cooperatives'))



if __name__ == '__main__':
    app.run(debug=True)