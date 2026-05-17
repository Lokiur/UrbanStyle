from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
import database as db


template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'APP_FlASK_MVC_URBANSTYLE', 'templates')

app = Flask(__name__, template_folder = template_dir)

# ingreso el login entrada al sistema progrma login flask

app.secret_key = 'supersecretkey'  # Clave para manejar las sesiones

# Configuración de la conexión a la base de datos MySQL
#db = mysql.connector.connect(
#  host="localhost",
#  user="root",
#  password="",
#  database="empresapy"
#)
#cursor = db.cursor(dictionary=True)

cursor = db.database.cursor(dictionary=True)

# Ruta para mostrar el formulario de login
@app.route('/')
def index():
  return render_template('login.html')

# Ruta para manejar el login
@app.route('/login', methods=['POST'])
def login():
  username = request.form['username']
  password = request.form['password']

  cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
  user = cursor.fetchone()

  if user:
      session['username'] = user['username']
      return redirect('/dashboard')
  else:
      return render_template('login.html', message='Credenciales incorrectas, inténtalo de nuevo.')

# Ruta protegida: solo accesible si el usuario ha iniciado sesión
@app.route('/dashboard')
def dashboard():
  if 'username' in session:
     # return f"Bienvenido, {session['username']}! Has iniciado sesión."
     return redirect('/home') 
  else:
      return redirect('/')

# Ruta para cerrar la sesión
@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect('/')


# termino la copia del login flask
"""
@app.route('/')

def principal ():
    return  " Bienvenido a mi página Web en Python"

@app.route('/contacto')

def contacto ():
    return  " esta es la página de contacto"

"""


@app.route('/')


def principal ():
    return render_template ('index.html')



@app.route('/lenguajes')

def mostrarLenguajes ():
     MisLenguajes = ("PHP", "PYTHON", "Java", "c#", "JavaScrip", "Perl", "Ruby", "Rust")
     return render_template ('lenguajes.html', lenguajes=MisLenguajes)

"""

@app.route('/login')

def login ():
     return render_template ('login.html')

"""

@app.route('/contacto')

def contacto ():
     return render_template ('contacto.html')

#Ruta para mi currículum
@app.route('/micurriculum')

def micurriculum ():
     return render_template ('micurriculum.html')



#Rutas de la aplicación MVC modelo vista controlador
@app.route('/home')
def home():
    cursor = db.database.cursor()
    

    cursor.execute("SELECT * FROM users")
    myresult = cursor.fetchall()
    #Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template('indexmvc.html', data=insertObject)

#Ruta para guardar usuarios en la bdd
@app.route('/user', methods=['POST'])
def addUser():
    username = request.form['username']
    name = request.form['name']
    apellidos = request.form['apellidos']
    password = request.form['password']
    usuario_email = request.form['usuario_email']
    celular = request.form['celular']
    fechanaci = request.form['fechanaci']

    if username and name and apellidos and password and usuario_email and celular and fechanaci:
        cursor = db.database.cursor()
        sql = "INSERT INTO users (username, name, apellidos, password, usuario_email, celular, fechanaci) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data = (username, name, apellidos, password, usuario_email, celular, fechanaci)
        cursor.execute(sql, data)
        db.database.commit()
    return redirect(url_for('home'))

@app.route('/delete/<string:id>')
def delete(id):
    cursor = db.database.cursor()
    sql = "DELETE FROM users WHERE id=%s"
    data = (id,)
    cursor.execute(sql, data)
    db.database.commit()
    return redirect(url_for('home'))

@app.route('/edit/<string:id>', methods=['POST'])
def edit(id):
    username = request.form['username']
    name = request.form['name']
    apellidos = request.form['apellidos']
    password = request.form['password']
    usuario_email = request.form['usuario_email']
    celular = request.form['celular']
    fechanaci = request.form['fechanaci']

    if username and name and apellidos and  password and usuario_email and celular and fechanaci:
        cursor = db.database.cursor()
        sql = "UPDATE users SET username = %s, name = %s, apellidos = %s, password = %s, usuario_email = %s, celular = %s, fechanaci = %s WHERE id = %s"
        data = (username, name, apellidos, password, usuario_email, celular, fechanaci, id)
        cursor.execute(sql, data)
        db.database.commit()
    return redirect(url_for('home'))



# Ejecutando el objeto Flask
if __name__ == '__main__':
    app.run(debug=True, port=5600)