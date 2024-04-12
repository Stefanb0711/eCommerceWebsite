from flask import Flask, render_template, request, redirect, flash, url_for
from flask_wtf import FlaskForm
from sqlalchemy import ForeignKey
from wtforms.fields.simple import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email
#from flask_bootstrap import Bootstrap5
import os
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import paypalrestsdk
from dotenv import find_dotenv, load_dotenv

app = Flask(__name__)


paypalrestsdk.configure({
  "mode": "sandbox",  # Sandbox-Modus für Tests
  "client_id": os.getenv("CLIENT_ID"),
  "client_secret": os.getenv("CLIENT_SECRET")
})




app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///customer.db"
db = SQLAlchemy()

db.init_app(app)

login_manager = LoginManager()

login_manager.init_app(app)


dotenv_path = find_dotenv()

load_dotenv(dotenv_path)



@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(user_id)




#app.config["SECRET_KEY"] = os.environ.get("MY_PASSWORD")



app.config['SECRET_KEY'] = os.getenv("SECRET_KEY_APP")

class Customer(UserMixin, db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    orders = relationship("Order", back_populates="customer")



class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    customer = relationship("Customer", back_populates="orders")
    total_sum = db.Column(db.Float, nullable=False)
    products = relationship("Products", back_populates="order")



class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200) , nullable=False)
    product_price = db.Column(db.String(200), nullable= False)
    quantity = db.Column(db.Integer, nullable=False)
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

total_price = 0

products = {
    "images" : ["/static/Pics/ProteinPizza.webp", "/static/Pics/ProteinPudding.webp", "/static/Pics/Proteinriegel.jpg", "/static/Pics/ProteinriegelSchwarz.jpg", "/static/Pics/Proteinshake.jpg", "/static/Pics/Proteinspaghetti.webp"],
    "titles" : ["Protein Pizza", "Protein Pudding", "Proteinriegel", "Proteinriegel Crispy", "Proteinshake", "Protein Spaghetti"],
    "prices" : ["5", "7", "15", "15", "7", "5"]

}

shopping_cart = {
    "product_images": [],
    "product_titles": [],
    "product_prices": [],
    "product_amounts" : []
}

@app.route('/', methods=['GET', 'POST'])
def start():  # put application's code here

    if request.method == 'POST':
        #amount_product = request.form.get("qty")

        """current_product_image = request.args.get("product_image")
        current_product_title = request.args.get("product_title")
        current_product_price = request.args.get("product_price")"""

        return redirect(url_for('shopping_cart_site'))

    return render_template("start.html", products=products)



@app.route('/einloggen', methods=['GET', 'POST'])
def login():

    login_form = LogInForm()


    if request.method == "POST":

        if request.form["username"] == "":
            flash("Das Feld Benutzer ist leer")

        elif request.form["password"] == "":
            flash("Das Feld Passwort ist leer")



        login_username = request.form["username"]
        user = Customer.query.filter_by(username = login_username).first()
        if user:

            if check_password_hash(user.password, request.form["password"]):
                login_user(user)
                return redirect(url_for("start"))

            else:
                flash("Das eingegebene Passwort ist falsch")

        else:
            flash("Der eingegebene Benutzername ist falsch. Probieren Sie es nochmal")






        """if customer_email and customer_password:
            flash("Logged in successfully!", "success")
        else:
            flash("Invalid")"""


    return render_template("anmelden.html", login_form = login_form)


@app.route('/registrieren', methods=['GET', 'POST'])
def register():

    register_form = RegisterForm()

    if request.method == "POST":
        register_email_adress = request.form["email"]
        register_username = request.form["username"]
        register_password = request.form["password"]

        if Customer.query.filter_by(username = register_username).first() or Customer.query.filter_by(email = register_email_adress).first():
            flash("Der Benutzername oder die Email-adresse existieren bereits. Probieren Sie was anderes aus")
        else:

            new_customer = Customer(
                username = register_username,
                email = register_email_adress,
                password = generate_password_hash(register_password, method='pbkdf2:sha1', salt_length=8)
            )

            db.session.add(new_customer)
            db.session.commit()

            login_user(new_customer)


            return redirect(url_for("start"))

    return render_template("registrieren.html", register_form = register_form)



@app.route('/warenkorb', methods=['GET', 'POST'])
#@login_required
def shopping_cart_site():
    global total_price
    total_price = 0



    product_image = request.form["product_image"]
    product_price = request.form["product_price"]
    product_title = request.form["product_title"]
    product_amount = request.form["qty"]


    shopping_cart["product_images"].append(product_image)
    shopping_cart["product_prices"].append(int(product_price))
    shopping_cart["product_titles"].append(product_title)
    shopping_cart["product_amounts"].append(int(product_amount))

    print(f"Product Amount: {product_amount}")


    for _ in range(len(shopping_cart["product_images"])):
        total_price += (shopping_cart["product_prices"][_] * shopping_cart["product_amounts"][_])

    print(f"Gesamtpreis: {total_price}")


        #Paypalbutton gedrückt
    



    return render_template("warenkorb.html", shopping_cart = shopping_cart, total_price = total_price)





# Route für die Zahlungsseite
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    global total_price

    if request.method == 'POST':
        # Betrag und Währung aus dem Formular erhalten
        amount = total_price
        currency = "EUR"

        # Erstellen Sie ein Zahlungsobjekt mit PayPal
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": amount,
                    "currency": currency
                },
                "description": "Zahlung"
            }],
            "redirect_urls": {
                "return_url": "http://localhost:5000/payment/execute",
                "cancel_url": "http://localhost:5000/payment/cancel"
            }
        })

        # Versuchen Sie, die Zahlung zu erstellen
        if payment.create():
            # Erfolgreich erstellt, leiten Sie zur PayPal-Zahlungsseite weiter
            for link in payment.links:
                if link.method == "REDIRECT":
                    return redirect(link.href)
        else:
            # Fehler beim Erstellen der Zahlung
            return str(payment.error)

    return render_template('payment.html')

@app.route("/payment/execute")
def execute_payment():
    # Bestätigen Sie die Zahlung
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        # Zahlung erfolgreich ausgeführt
        return redirect(url_for("success"))
    else:
        # Fehler bei der Zahlungsausführung
        return str(payment.error)



@app.route("/payment_successfull", methods=['GET', 'POST'])
def success():

    if request.method == "POST":
        return redirect(url_for("start"))
    return render_template('success.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("start"))


if __name__ == '__main__':
    app.run()