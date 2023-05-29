"""initialize basic prototype file in which website ask for input data
 and directly after input ,it generates the qr as output as a png file"""
from flask import Flask, render_template, request, send_file
import qrcode

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index_practice.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form['data']

    # Error handling for empty data
    if not data:
        return render_template('index_practice.html', error='Please enter data')

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img_path = 'static/qr_code.png'
    img.save(img_path)

    return render_template('result_practice.html', img_path=img_path)

@app.route('/download')
def download():
    return send_file('static/qr_code.png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
