from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = "cliente"
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    
    pedidos = db.relationship('Pedidos', backref='cliente', lazy=True)
    
class Pedidos(db.Model):
    __tablename__ = "pedidos"
    
    id = db.Column(db.Integer, primary_key=True)
    idCliente = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    tamanoPizza = db.Column(db.String(10))
    ingredientes = db.Column(db.String(50))
    numPizzas = db.Column(db.Integer)
    fechaPedido = db.Column(db.Date)
    subTotal = db.Column(db.Float)
    total = db.Column(db.Float)


# importamos UserMixin de flask_login que nos permite tener un objeto de usuario con atributos y metodos predefinidos
from flask_login import UserMixin
# importamos generate_password_hash y check_password_hash de werkzeug.security para encriptar y comparar contraseñas
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    # creamos un constructor con los atributos id, nombre, email, contrasenia 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100))
    #generate_password_hash(contrasenia)
    contrasenia = db.Column(db.String(100))
    rol = db.Column(db.String(30))

    # enctripta y almacena la contraseña
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    # compara la contraseña encriptada con la contraseña ingresada por el usuario para verificar si es correcta
    def check_password(self, password):
        return check_password_hash(self.password, password)
    