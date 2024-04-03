from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey
from wtforms.fields.simple import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_bootstrap import Bootstrap5
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///customer.db"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)



#app.config["SECRET_KEY"] = os.environ.get("MY_PASSWORD")
db.init_app(app)


bootstrap = Bootstrap5(app)

app.config['SECRET_KEY'] = 'SECRET'

class Customer(UserMixin, db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    orders = relationship("Products", back_populates="order")



class Order(UserMixin, db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    customer = relationship("Customer", back_populates="orders")

    products = relationship("Products", back_populates="order")



class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200) , nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    order = relationship("Order", back_populates="products")






with app.app_context():
    db.create_all()



class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Registrieren')

class LogInForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Anmelden')



products = {
    "images" : ["/static/Pics/ProteinPizza.webp", "/static/Pics/ProteinPudding.webp", "/static/Pics/Proteinriegel.jpg", "/static/Pics/ProteinriegelSchwarz.jpg", "/static/Pics/Proteinshake.jpg", "/static/Pics/Proteinspaghetti.webp"],
    "titles" : ["Protein Pizza", "Protein Pudding", "Proteinriegel, Proteinriegel Schwarz", "Proteinshake", "Protein Spaghetti"]
}

@app.route('/', methods=['GET', 'POST'])
def start():  # put application's code here


    return render_template("start.html", products=products)



@app.route('/einloggen', methods=['GET', 'POST'])
def login():

    login_form = LogInForm()


    if request.method == "POST":

        return redirect(url_for("start"))

    return render_template("Anmelden.html", login_form = login_form)


@app.route('/registrieren', methods=['GET', 'POST'])
def register():

    register_form = RegisterForm()

    if request.method == "POST":

        return redirect(url_for("start"))

    return render_template("Registrieren.html", register_form = register_form)


if __name__ == '__main__':
    app.run()
