from flask import Flask

app = Flask(__name__)

@app.route('/<username>')
def home(username):
    return f"Hello, {username}!"

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

if __name__ == '__main__':
    app.run(debug=True)


