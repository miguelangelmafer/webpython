import os
from flask import Flask
from flask import render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

app=Flask(__name__)
app.secret_key="develoteca"
mysql=MySQL()


# Configuración a la BD
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='webpython'
mysql.init_app(app)

# Rutas que redireccionan a templates html

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/Sitio/img'),imagen)

@app.route('/libros')
def libros():

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)

    return render_template('sitio/libros.html', libros=libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)

    if _usuario=="admin" and _password=="123456":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template('admin/login.html')

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')


@app.route('/admin/libros')
def admin_libros():
    # Recuperación datos en BD
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)

    return render_template('admin/libros.html',libros=libros)

# Permite la recepción de inputs de un formulario
@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():
    _nombre = request.form['txtNombre']
    _url = request.form['txtURL']
    _archivo = request.files['txtImagen']

    tiempo = datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')

    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/" + nuevoNombre)

    # Inserción datos en BD
    sql ="INSERT INTO `libros` (`id`,`nombre`,`imagen`,`url`) VALUES (NULL,%s,%s,%s);"
    datos=(_nombre,nuevoNombre,_url)
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    print(_nombre)
    print(_url)
    print(_archivo)

    return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():
    _id=request.form['txtID']
    print(_id)

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("SELECT imagen FROM `libros` WHERE id=%s",(_id))
    libro=cursor.fetchall()
    conexion.commit()
    print(libro)

    #Borra la imagen de la carpeta img
    if(os.path.exists("templates/sitio/img/"+str(libro[0][0]))):
        os.unlink("templates/sitio/img/"+str(libro[0][0]))

    # Borrar datos en BD
    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM `libros` WHERE id=%s",(_id))
    conexion.commit()

    return redirect('/admin/libros')


if __name__ == '__main__':
    app.run(debug=True)
    
