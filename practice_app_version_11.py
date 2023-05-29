"""In last 10 versions, when i was using heading so some input data is getting
out of image so i used a textwrap module for wrapping of text

"""
import os
import textwrap
from flask import Flask, render_template, request, send_file, session
import qrcode
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter



app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route('/')
def index():
    return render_template('index_color_10.html')


@app.route('/generate', methods=['POST'])
def generate():
    data = request.form['data']
    upload = request.files['upload']
    heading = request.form['heading']
    color = request.form.get('color', 'black')
    background = request.form.get('background', 'white')
    heading_color = request.form.get('heading_color', 'black')  # Retrieve heading color option

    if not data:
        return render_template('index_color_10.html', error='Please enter data')

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=color, back_color=background)

    # Calculate the size of the symbol/logo based on the length of the input string
    symbol_size = min(max(len(data) // 2, 50), 200)

    # Add symbol/logo to the center of the QR code if uploaded
    if upload:
        logo = Image.open(upload)
        logo.thumbnail((symbol_size, symbol_size), Image.ANTIALIAS)

        qr_size = img.size[0] - (2 * qr.border)
        symbol_position = (
            (qr_size - logo.size[0]) // 2,
            (qr_size - logo.size[1]) // 2
        )

        img.paste(logo, symbol_position)

    # Wrap heading text to multiple lines
    if heading:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 20)
        max_width = img.size[0] - 20  # Adjust maximum width for padding
        wrapped_lines = textwrap.wrap(heading, width=max_width // font.getsize('x')[0])

        # Calculate total height for wrapped text
        total_height = len(wrapped_lines) * font.getsize('x')[1]

        # Calculate starting position for wrapped text
        start_y = (img.size[1] - total_height) - 10

        # Draw each line of wrapped text
        for line in wrapped_lines:
            line_width, line_height = draw.textsize(line, font=font)
            line_position = ((img.size[0] - line_width) // 2, start_y)
            draw.text(line_position, line, fill=heading_color, font=font)
            start_y += line_height

    img_buffer = BytesIO()
    img.save(img_buffer, 'PNG')
    img_buffer.seek(0)

    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    # Store img base64-encoded string in session
    session['img_base64'] = img_base64

    return render_template('result_color_10.html', qr_code=img_base64, heading_color=heading_color)


@app.route('/download', methods=['POST'])
def download():
    qr_code = request.form['qr_code']
    file_type = request.form['file_type']
    heading = request.form['heading']
    heading_color = request.form['heading_color']  # Retrieve heading color option

    # Create a BytesIO object from the base64 encoded image data
    img_data = base64.b64decode(qr_code)
    img_buffer = BytesIO(img_data)

    if file_type == 'png':
        return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name='qr_code.png')
    elif file_type == 'pdf':
        # Create a new PDF
        pdf_buffer = BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer)

        # Draw the QR code image on the PDF canvas
        qr_page = Image.open(img_buffer)
        qr_page.save('qr_code.png')  # Save the image temporarily

        # Calculate the center coordinates for the QR code image in the PDF
        pdf_width, pdf_height = pdf_canvas._pagesize
        qr_width, qr_height = qr_page.size
        image_x = (pdf_width - qr_width) / 2
        image_y = (pdf_height - qr_height) / 2

        pdf_canvas.drawImage('qr_code.png', image_x, image_y, width=qr_width, height=qr_height)
        os.remove('qr_code.png')  # Remove the temporary image file

        # Add heading to the PDF with the specified color
        if heading:
            pdf_canvas.setFont('Helvetica', 24)
            pdf_canvas.setFillColor(heading_color)  # Set the heading color
            text_width = pdf_canvas.stringWidth(heading, 'Helvetica', 24)
            x_coordinate = (letter[0] - text_width) / 2  # Calculate X-coordinate for center alignment
            pdf_canvas.drawString(x_coordinate, 730, heading)  # Adjust Y-coordinate as needed

        # Save the PDF canvas and close it
        pdf_canvas.save()

        pdf_buffer.seek(0)

        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='qr_code.pdf')


if __name__ == '__main__':
    app.run(debug=True)
