"""In the first version, i upgraded the code with heading in the qr code and download option for png image
but it failed due to some errors in byte stream during transfer of data for the qr code and connecting
it with heading data"""
from flask import Flask, render_template, request, send_file
import qrcode
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index_practice.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form['data']
    heading = request.form['heading']

    # Error handling for empty data
    if not data:
        return render_template('index_practice.html', error='Please enter data')

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Add heading text above the QR code
    if heading:
        heading_font = qrcode.image.font.Font(size=20)
        heading_width, heading_height = heading_font.getsize(heading)
        heading_img = qrcode.image.ImageWriter()
        heading_img.add_data(heading)
        heading_img_img = heading_img.make_image(heading_font=heading_font)

        # Calculate the position to center the heading image on the QR code
        qr_width, qr_height = img.size
        heading_x = int((qr_width - heading_width) / 2)
        heading_y = int((qr_height - heading_height) / 2)

        # Paste the heading image onto the QR code
        img.paste(heading_img_img, (heading_x, heading_y))

    # Create a BytesIO object to hold the image data in memory
    img_buffer = BytesIO()
    img.save(img_buffer, 'PNG')

    # Set the buffer's position to the start of the stream
    img_buffer.seek(0)

    return render_template('result_practice.html', qr_code=img_buffer.getvalue().decode('utf-8'), heading=heading)

@app.route('/download', methods=['POST'])
def download():
    qr_code = request.form['qr_code']

    # Create a BytesIO object from the base64 encoded image data
    img_buffer = BytesIO(qr_code.encode('utf-8'))

    return send_file(img_buffer, mimetype='image/png', as_attachment=True, attachment_filename='qr_code.png')

if __name__ == '__main__':
    app.run(debug=True)
