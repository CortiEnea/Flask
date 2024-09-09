from models.conn import db
from werkzeug.security import generate_password_hash, check_password_hash
    
class QrData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(120), unique=True, nullable=False)
    color = db.Column(db.String(10), unique=True, nullable=False)
