from flask import Flask
from flask import render_template
from flask import request
from flask import Flask
from flask_migrate import Migrate
from models.conn import db
from models.model import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://hello_flask_adm:Admin$00@localhost/flask_hello'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

migrate = Migrate(app, db)



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
    url = values["url"]
    color = values["color"]
    url_qr = f"http://api.qrserver.com/v1/create-qr-code/?data={url}"
    save_qr_data(url=url, color=color)
    return render_template('qr_generator.html', url_qr=url_qr)

def save_qr_data(url, color):
    qr = QrData(link=url, color=color)
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


if __name__ == '__main__':
    app.run(debug=True)


