"""in version 4 when we are trying to add symbol ,the symbol was getting added
 to center of image+border size instead of center of qr code so tried a new method to add it in center"
"""
import os
import img2pdf
from flask import Flask, render_template, request, send_file
import qrcode
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index_practice.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form['data']
    upload = request.files['upload']

    # Error handling for empty data
    if not data:
        return render_template('index_practice.html', error='Please enter data')

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Add symbol/logo to the center of the QR code if uploaded
    if upload:
        logo = Image.open(upload)
        basewidth = 100
        wpercent = (basewidth / float(logo.size[0]))
        hsize = int(float(logo.size[1]) * float(wpercent))
        logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)

        qr_size = img.size[0] - (2 * qr.border)
        symbol_position = (
            (qr_size - logo.size[0]) // 2,
            (qr_size - logo.size[1]) // 2
        )

        img.paste(logo, symbol_position)

    img_buffer = BytesIO()
    img.save(img_buffer, 'PNG')
    img_buffer.seek(0)

    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    return render_template('result_practice.html', qr_code=img_base64)


@app.route('/download', methods=['POST'])
def download():
    qr_code = request.form['qr_code']
    file_type = request.form['file_type']

    # Create a BytesIO object from the base64 encoded image data
    img_data = base64.b64decode(qr_code)
    img_buffer = BytesIO(img_data)

    if file_type == 'png':
        return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name='qr_code.png')
    elif file_type == 'pdf':
        # Convert the QR code image to PDF using img2pdf
        pdf_buffer = BytesIO()
        pdf_file_name = 'qr_code.pdf'

        # Create a PDF with the QR code image
        with open(pdf_file_name, "wb") as f:
            f.write(img2pdf.convert(img_buffer.getvalue()))

        # Read the generated PDF file and send it as a response
        with open(pdf_file_name, 'rb') as f:
            pdf_buffer.write(f.read())

        pdf_buffer.seek(0)

        # Remove the temporary PDF file
        os.remove(pdf_file_name)

        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True,  download_name=pdf_file_name)

if __name__ == '__main__':
    app.run(debug=True)
