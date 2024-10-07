from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import current_app   # definisce il contesto del modulo
from flask_login import login_user  # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
from flask_login import login_required
from flask_login import current_user
from flask_login import logout_user
from werkzeug.utils import secure_filename

import os

from models.conn import db
from models.model import *


qrcode = Blueprint('qr', __name__)



ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@qrcode.route('/qr')
def qr():
     return render_template('QR/create_qr.html')

@qrcode.route('/generate_qr/',methods=['POST'])
def generate_qr():  
    name = request.form["name"]
    url = request.form["url"]
    color = request.form["color"]
    back = request.form["backcolor"]
    file = request.files['icon_img']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    save_qr_data(name=name,url=url, color=color, back=back,file=filename)
    return render_template('QR/qr_result.html', url=url, color=color, back=back, file=filename)


def save_qr_data(name, url, color, back, file):
    qr = QrData(name=name, link=url, color=color, back=back, filename=file)
    db.session.add(qr)  # equivalente a INSERT
    db.session.commit() 
    return f"Qr per il seguente link creato con successo: {qr.link}"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@qrcode.route('/history')
def history():
    qrcodes = QrData.query.all()
    return render_template('QR/qr_history.html', qrcodes=qrcodes)