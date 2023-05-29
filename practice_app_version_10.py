# in version 10,i added color option in headings of pdf file during download option
import os
from flask import Flask, render_template, request, send_file
import qrcode
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


app = Flask(__name__)

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

    # Add heading to the image with the specified color
    if heading:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 20)
        text_width, text_height = draw.textsize(heading, font=font)
        text_position = ((img.size[0] - text_width) // 2, img.size[1] - text_height - 10)
        draw.text(text_position, heading, fill=heading_color, font=font)  # Use heading_color

    img_buffer = BytesIO()
    img.save(img_buffer, 'PNG')
    img_buffer.seek(0)

    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

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
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)

        # Draw the QR code image on the PDF canvas
        qr_page = Image.open(img_buffer)
        qr_page.save('qr_code.png')  # Save the image temporarily
        pdf_canvas.drawImage('qr_code.png', 0, 0, width=letter[0], height=letter[1])
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
