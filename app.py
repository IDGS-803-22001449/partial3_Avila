from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from models import db, Pedidos, Cliente, User
from datetime import date
import datetime

# desde la libreria de flask_login importamos LoginManager
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
# dentro de la libreria se necesita una llave secreta de encriptacion, 
# la cual tomaremos la ayuda de la libreria secrets para crear una aleatoria de manera mas segura

from forms import LoginForm

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)


# creamos una instancia de LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# por medio de app.config llamamos a la llave secreta y le asignamos un valor aleatorio que generamos anteriormente
app.config['SECRET_KEY'] = '166bcd568a88a19a39cddf19e9493dd42d5fc320eeb72662d97829df07ea6f1d'


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



# Definir el user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()    
    if form.validate_on_submit():
        email = form.email.data.strip()
        contrasenia = form.contrasenia.data
        print(f"Usuario: {email}, Contraseña ingresada: {contrasenia}") 
        
        user = User.query.filter_by(email=email).first()  # Busca el usuario en la bd
        
        if user:
            print(f"Contraseña en la base de datos: {user.contrasenia}")
            
            
            if user.contrasenia == contrasenia:
                print("Contraseñas coinciden")
                login_user(user)
                flash(f'Bienvenido {user.nombre}', 'success')

                if user.rol == "admin":
                    return redirect(url_for('index'))
                elif user.rol == "cliente":
                    return redirect(url_for('buscarPedidos'))
                else:
                    flash("No tienes permiso para acceder", "danger")
                    return redirect(url_for('login'))
            else:
                print("Contraseñas no coinciden")
                flash('Usuario o contraseña incorrecta', 'danger')
        else:
            flash('Usuario o contraseña incorrecta', 'danger')

    return render_template('login.html', form=form)





@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/index", methods=['GET', 'POST'])
# autenticacion de usuario
@login_required
def index():
    pedidos = []
    total = 0
    nombre = ""
    
    
    if current_user.rol == "cliente":
        flash("No tienes permiso para acceder a esta página.", "danger")
        return redirect(url_for('buscarPedidos'))
    
    try:
        with open("pedidos.txt", "r") as file:
            pedidos = [eval(line.strip()) for line in file.readlines()]
            total = sum(p['subtotal'] for p in pedidos)
    except FileNotFoundError:
        pass
    
    if request.method == 'POST':
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        telefono = request.form.get("telefono")
        numeroPizzas = int(request.form.get("numeroPizzas"))
        tamanoPizza = request.form.get("tamanopizza")
        ingredientes = request.form.getlist("ingredientes")
        fechaPedido = request.form.get('fechaPedido')
        
        if fechaPedido:
            fechaPedido = datetime.datetime.strptime(fechaPedido, '%Y-%m-%d').date()
        
        pedido = {
            "nombre": nombre,
            "direccion": direccion,
            "telefono": telefono,
            "numeroPizzas": numeroPizzas,
            "tamanoPizza": tamanoPizza,
            "ingredientes": ingredientes,
            "subtotal": calcSubtotal(tamanoPizza, ingredientes, numeroPizzas),
            "fechaPedido": fechaPedido
        }
        
        with open("pedidos.txt", "a") as file:
            file.write(str(pedido) + "\n")
        
        return redirect(url_for('index'))
    
    return render_template("index.html", pedidos=pedidos, total=total, nombre=nombre)

@app.route("/importarPedidos", methods=['POST'])
def importarPedidos():
    try:
        with open("pedidos.txt", "r") as file:
            pedidos = [eval(line.strip()) for line in file.readlines()]
        
        for pedido in pedidos:
            subtotal = calcSubtotal(pedido['tamanoPizza'], pedido['ingredientes'], pedido['numeroPizzas'])

            cliente = Cliente.query.filter_by(nombre=pedido['nombre']).first()
            
            if not cliente:
                cliente = Cliente(
                    nombre=pedido['nombre'],
                    direccion=pedido['direccion'],
                    telefono=pedido['telefono']
                )
                db.session.add(cliente)
                db.session.commit()
            
            nuevo_pedido = Pedidos(
                idCliente=cliente.id,
                tamanoPizza=pedido['tamanoPizza'],
                ingredientes=", ".join(pedido['ingredientes']),
                numPizzas=pedido['numeroPizzas'],
                fechaPedido=pedido['fechaPedido'],
                subTotal=subtotal,
                total=subtotal
            )
            
            db.session.add(nuevo_pedido)
        
        db.session.commit()

        with open("pedidos.txt", "w") as file:
            file.truncate(0)


    except Exception as e:
        flash(f"Error al importar pedidos: {str(e)}", "danger")

    return redirect(url_for('index'))


@app.route("/eliminarPedido", methods=['POST'])
def eliminarPedido():
    try:
        with open("pedidos.txt", "r") as file:
            pedidos = file.readlines()

        if pedidos:
            pedidos.pop()

            with open("pedidos.txt", "w") as file:
                file.writelines(pedidos)

        else:
            flash("No hay pedidos para eliminar.", "warning")

    except Exception as e:
        flash(f"Error al eliminar pedido: {str(e)}", "danger")

    return redirect(url_for('index'))

def calcSubtotal(tamanoPizza, ingredientes, numPizzas):
    precios = {"Chica": 40, "Mediana": 80, "Grande": 120}

    tamanoPizza = tamanoPizza.capitalize()

    precioPizza = precios.get(tamanoPizza, 0)
    if precioPizza == 0:
        raise ValueError(f"Tamaño de pizza inválido: {tamanoPizza}")

    subtotal = int((precioPizza + len(ingredientes) * 10) * numPizzas)
    
    return subtotal

@app.route("/buscarPedidos", methods=['GET'])
def buscarPedidos():
    fecha_busqueda = request.args.get('fecha')
    
    if fecha_busqueda:
        try:
            fecha_busqueda = datetime.datetime.strptime(fecha_busqueda, '%Y-%m-%d').date()

            pedidos = Pedidos.query.filter(Pedidos.fechaPedido == fecha_busqueda).all()

            if not pedidos:
                flash("No se encontraron pedidos para esa fecha.", "warning")

            return render_template("buscarPedidos.html", pedidos=pedidos, fecha_busqueda=fecha_busqueda)

        except ValueError:
            flash("Fecha inválida, por favor usa el formato yyyy-mm-dd", "danger")
            return redirect(url_for('buscarPedidos'))
        
    pedidos = Pedidos.query.all()

    return render_template("buscarPedidos.html", pedidos=pedidos, fecha_busqueda=None)


if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
