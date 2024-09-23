from models.conn import db
from flask_login import UserMixin
#from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt 
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


bcrypt = Bcrypt() 
  
class QrData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(120), unique=True, nullable=False)
    color = db.Column(db.String(10), unique=True, nullable=False)

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128)) 

    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash (password).decode('utf-8') 

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    



def init_db():  #nuovo stile
    # Verifica se i ruoli esistono già
    if not db.session.execute(db.select(Role).filter_by(name='admin')).scalars().first():
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()

    if not db.session.execute(db.select(Role).filter_by(name='user')).scalars().first():
        user_role = Role(name='user')
        db.session.add(user_role)
        db.session.commit()

    # Verifica se l'utente admin esiste già
    if not db.session.execute(db.select(User).filter_by(username='admin')).scalars().first():
        admin_user = User(username="admin", email="admin@example.com")
        admin_user.set_password("adminpassword")
        
        # Aggiunge il ruolo 'admin' all'utente
        admin_role = db.session.execute(db.select(Role).filter_by(name='admin')).scalars().first()
        admin_user.roles.append(admin_role)

        db.session.add(admin_user)
        db.session.commit()

def user_has_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Devi essere autenticato per accedere a questa pagina.")
                return redirect(url_for('login'))
            if not current_user.has_role(role_name):
                flash("Non hai il permesso per accedere a questa pagina.")
                return abort(403)  # Restituisce un errore 403 Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator