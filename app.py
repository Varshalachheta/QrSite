"""If you want to know how i made this file then check all practice version till last,
the last version is in the app file"""

import os
import textwrap
from flask import Flask, render_template, request, send_file, session
import qrcode
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import secrets



app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    #collecting input values
    data = request.form['data']
    upload = request.files['upload']
    heading = request.form['heading']
    color = request.form.get('color', 'black')
    background = request.form.get('background', 'white')
    heading_color = request.form.get('heading_color', 'black')

    if not data:
        return render_template('index.html', error='Please enter data')

    # Create a QRCode object
    qr = qrcode.QRCode(version=1, box_size=10, border=5)

    # Add the data to the QRCode object
    qr.add_data(data)

    # Generate the QR code image
    qr.make(fit=True)

    # Create the image from the QRCode object with specified fill and background colors
    img = qr.make_image(fill_color=color, back_color=background)


    # Add symbol/logo to the center of the QR code if uploaded
    if upload:
        logo = Image.open(upload)

        # Calculate the maximum size for the symbol/logo based on the length of the data
        symbol_size = min(max(len(data) // 2, 50), 200)

        # Calculate the scale factor to resize the symbol/logo while maintaining its aspect ratio
        scale_factor = min(symbol_size / logo.width, symbol_size / logo.height)

        # Calculate the new width and height of the logo based on the scale factor
        new_width = int(logo.width * scale_factor)
        new_height = int(logo.height * scale_factor)

        # Resize the logo image using the new width and height
        logo = logo.resize((new_width, new_height), Image.ANTIALIAS)

        # Calculate the position to place the symbol/logo
        qr_size = img.size[0] - (2 * qr.border)
        symbol_position = (
            (qr_size - logo.size[0]) // 2,
            (qr_size - logo.size[1]) // 2
        )

        # Create a new image with the symbol/logo overlaying the QR code
        qr_with_logo = img.copy()  # Create a copy of the original QR code image
        qr_with_logo.paste(logo, symbol_position)  # Overlay the logo image onto the QR code image

        img = qr_with_logo  # Update the image variable with the QR code image containing the logo

    # Wrap heading text to multiple lines
    # Wrap heading text to multiple lines
    if heading:
        draw = ImageDraw.Draw(img)  # Create a drawing object to draw on the image
        font = ImageFont.truetype("arial.ttf", 20)  # Load the desired font with size 20
        max_width = img.size[0] - 20  # Adjust maximum width for padding

        # Calculate the maximum number of characters that can fit in a line based on the font size
        chars_per_line = max_width // font.getsize('x')[0]

        # Wrap the heading text into multiple lines using the calculated character limit per line
        wrapped_lines = textwrap.wrap(heading, width=chars_per_line)

        # Calculate total height for wrapped text
        total_height = len(wrapped_lines) * font.getsize('x')[1]

        # Calculate starting position for wrapped text
        start_y = (img.size[1] - total_height) - 10

        # Draw each line of wrapped text
        for line in wrapped_lines:
            # Calculate the width and height of the line of text
            line_width, line_height = draw.textsize(line, font=font)

            # Calculate the position to center-align the line of text horizontally
            line_position = ((img.size[0] - line_width) // 2, start_y)

            # Draw the line of text on the image using the specified font, position, and color
            draw.text(line_position, line, fill=heading_color, font=font)

            # Update the starting position for the next line of text
            start_y += line_height

    img_buffer = BytesIO()  # Create a BytesIO object to store the image data
    img.save(img_buffer, 'PNG')  # Save the image to the img_buffer in PNG format
    img_buffer.seek(0)  # Set the file pointer to the beginning of the buffer

    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')  # Encode the image data in base64 format and decode it to a string


    # Store img base64-encoded string in session
    session['img_base64'] = img_base64

    return render_template('result.html', qr_code=img_base64, heading_color=heading_color)


@app.route('/download', methods=['POST'])
def download():
    #collecting input values
    qr_code = request.form['qr_code']
    file_type = request.form['file_type']
    heading = request.form['heading']
    heading_color = request.form['heading_color']

    # Create a BytesIO object from the base64 encoded image data
    img_data = base64.b64decode(qr_code)  # Decode the base64 encoded image data
    img_buffer = BytesIO(img_data)  # Create a BytesIO object to hold the image data


    if file_type == 'png':
        return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name='qr_code.png')
    elif file_type == 'pdf':
        # Create a new PDF
        pdf_buffer = BytesIO()  # Create a BytesIO buffer to store the PDF data
        pdf_canvas = canvas.Canvas(pdf_buffer)  # Create a canvas for drawing on the PDF

        # Draw the QR code image on the PDF canvas
        qr_page = Image.open(img_buffer)  # Open the QR code image from the BytesIO buffer
        qr_page.save('qr_code.png')  # Save the image temporarily as 'qr_code.png'
        # Note: The image is saved temporarily to disk because the ReportLab library requires a file path for image insertion.
        # Alternatively, we could use another BytesIO buffer to store the image data instead of saving it to disk.


        # Calculate the center coordinates for the QR code image in the PDF
        pdf_width, pdf_height = pdf_canvas._pagesize
        qr_width, qr_height = qr_page.size
        image_x = (pdf_width - qr_width) / 2
        image_y = (pdf_height - qr_height) / 2

        pdf_canvas.drawImage('qr_code.png', image_x, image_y, width=qr_width, height=qr_height)
        os.remove('qr_code.png')  # Remove the temporary image file

        # Add heading to the PDF with the specified color
        if heading:
            font_size = 20
            max_width = pdf_width - 2 * image_x
            font = ImageFont.truetype("arial.ttf", font_size)

            # Wrap heading text to fit within the maximum width
            wrapped_text = textwrap.fill(heading, width=int(max_width / font.getsize('x')[0]))

            # Reverse the list of wrapped lines
            reversed_lines = wrapped_text.split('\n')[::-1]

            # Calculate the height of the wrapped text
            line_height = font.getsize('x')[1]
            total_height = len(reversed_lines) * line_height

            # Calculate starting position for wrapped text at the top
            start_y = image_y + qr_height + 10

            # Draw each line of wrapped text in the correct order
            for line in reversed_lines:
                line_width, _ = font.getsize(line)#This line calculates the width of the current line of text using the getsize() method of the font object.This line calculates the width of the current line of text using the getsize() method of the font object. The width is assigned to the variable line_width. The underscore _ is used as a placeholder for the height of the text, which is not needed in this context.
                line_x = image_x + (max_width - line_width) / 2  # Center-align the text horizontally
                line_position = (line_x, start_y)
                pdf_canvas.setFont("Helvetica", font_size)
                pdf_canvas.setFillColor(heading_color)
                pdf_canvas.drawString(line_position[0], line_position[1], line)
                start_y += line_height

        # Save the PDF canvas and close it
        pdf_canvas.save()

        pdf_buffer.seek(0)  # Seek the beginning of the pdf_buffer stream

        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='qr_code.pdf')


if __name__ == '__main__':
    app.run(debug=True)
