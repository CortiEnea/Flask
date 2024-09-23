from flask import Flask
from flask import render_template
from flask import request
from flask import Flask
from flask_migrate import Migrate
from models.conn import db
from models.model import *
from flask_qrcode import QRcode
from flask_login import LoginManager
from routes.auth import auth as bp_auth
from flask_login import login_required
from dotenv import load_dotenv
import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.register_blueprint(bp_auth, url_prefix='/auth')
load_dotenv()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db.init_app(app)


migrate = Migrate(app, db)
QRcode(app)

class ProtectedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


migrate = Migrate(app, db)
admin = Admin(app, name='Admin dashboard')
admin.add_view(ProtectedModelView(User, db.session))


@app.route('/<username>')
def home(username):
    return f"Hello, {username}!"


@app.route('/hello/<username>')
def hello(username):
    return render_template('hello.html', username=username)

@app.route('/sum', methods=['POST'])
def sum():
    values = request.json
    v1 = values["v1"]
    v2 = values["v2"]
    return f'{v1+v2}'

@app.route('/generate_qr/',methods=['POST'])
def generate_qr():
    values = request.json
    name = values["name"]
    url = values["url"]
    color = values["color"]
    back = values["back_color"]
    icon_img = values["icon_img"]
    save_qr_data(name=name,url=url, color=color, back=back)
    return render_template('qr_generator.html', url=url, color=color, back=back, icon_img=icon_img)

def save_qr_data(name, url, color, back):
    qr = QrData(name=name, link=url, color=color, back=back)
    db.session.add(qr)  # equivalente a INSERT
    db.session.commit()
    return f"Qr per il seguente link creato con successo: {qr.link}"

@app.route('/test_user')
def test_user():
    # Creazione di un nuovo utente con una password criptata
    user = User(username='testuser', email='test@example.com')
    user.set_password('mysecretpassword')

    # Aggiunta dell'utente al database
    db.session.add(user)
    db.session.commit()

    # Verifica della password
    if user.check_password('mysecretpassword'):
        return"Password corretta!"
    else:
        return "Password errata!"
    
@app.route('/create_user',methods=['POST'])
def create_user():
#def create_user(username, email, password):
    values = request.json
    username = values["username"]
    email = values["email"]
    password = values["password"]
    user = User(username=username, email=email)
    user.set_password(password)  # Imposta la password criptata
    db.session.add(user)  # equivalente a INSERT
    db.session.commit()
    return f"Utente {username} creato con successo."

@app.route('/create_user2')
def create_user2():
#def create_user(username, email, password):
    username = "test"
    email = "bla"
    password = "pass"
    user = User(username=username, email=email)
    user.set_password(password)  # Imposta la password criptata
    db.session.add(user)  # equivalente a INSERT
    db.session.commit()
    return f"Utente {username} creato con successo."

@app.route('/find_by_username', methods=['POST'])
def find_by_username():
    values = request.json
    username = values["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        return f"Utente trovato: {user.username}, Email: {user.email}"
    else:
        return "Utente non trovato."
    
@app.route('/update_user', methods=['POST'])
def update_user_email():
    values = request.json
    username = values["username"]
    new_email = values["new_mail"]
    user = User.query.filter_by(username=username).first()
    if user:
        user.email = new_email
        db.session.commit()
        return f"Email aggiornata per {user.username}"
    else:
        return "Utente non trovato."
    
@app.route('/delete_user', methods=['POST'])
def delete_user_by_username():
    values = request.json
    username = values["username"]
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return f"Utente {username} eliminato."
    else:
        return "Utente non trovato."
    
# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    # return User.query.get(int(user_id))   # legacy
    
    return user

with app.app_context():
    init_db()

@app.route('/dashboard')
@login_required
@user_has_role('admin') # oppure @user_has_role('admin', 'moderator')
def admin_dashboard():
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)


