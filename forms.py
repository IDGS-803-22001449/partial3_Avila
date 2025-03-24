from wtforms import Form
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, validators, SubmitField, PasswordField
from wtforms.validators import DataRequired


class OrdenForm(Form):
    nombre = StringField('nombre')
    direccion = StringField('direccion')
    telefono = StringField('telefono')
    tamanoPizza = StringField('tamanoPizza')
    ingredientes = StringField('ingredientes')
    numPizzas = IntegerField('numPizzas')
    fechaPedido = StringField('fechaPedido')
    
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    contrasenia = PasswordField('Contraseña', validators=[DataRequired()])