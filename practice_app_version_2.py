"""the second version was upgrade of first version in which
 i used pillow module to solve image heading problem but there was a problem with download because it needs 64 bit base"""
from flask import Flask, render_template, request, send_file
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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
        heading_font = ImageFont.truetype('arial.ttf', size=20)
        heading_width, heading_height = ImageDraw.Draw(Image.new('RGB', (1, 1))).textsize(heading, font=heading_font)

        # Calculate the position to center the heading on the QR code
        qr_width, qr_height = img.size
        heading_x = int((qr_width - heading_width) / 2)
        heading_y = int((qr_height - heading_height) / 2) - 30

        # Create a new image with the heading text
        heading_img = Image.new('RGB', (qr_width, qr_height + 50), color='white')
        d = ImageDraw.Draw(heading_img)
        d.text((heading_x, heading_y), heading, fill='black', font=heading_font)

        # Combine the heading image and the QR code image
        combined_img = Image.new('RGB', (qr_width, qr_height + 50), color='white')
        combined_img.paste(img, (0, 50))
        combined_img.paste(heading_img, (0, 0))

        # Create a BytesIO object to hold the combined image data in memory
        img_buffer = BytesIO()
        combined_img.save(img_buffer, format='PNG')

    else:
        # Create a BytesIO object to hold the image data in memory
        img_buffer = BytesIO()
        img.save(img_buffer, 'PNG')

    # Set the buffer's position to the start of the stream
    img_buffer.seek(0)

    return render_template('result_practice.html', qr_code=img_buffer.getvalue(), heading=heading)


@app.route('/download', methods=['POST'])
def download():
    qr_code = request.form['qr_code']

    # Create a BytesIO object from the base64 encoded image data
    img_buffer = BytesIO(qr_code.encode('utf-8'))

    return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name='qr_code.png')

if __name__ == '__main__':
    app.run(debug=True)
