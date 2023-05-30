import numpy as np
from flask import Flask, request, render_template, session, send_from_directory, Response
import pickle
import base64
from PIL import Image, ImageEnhance, ImageOps
import io




app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Set a secret key for session encryption

# model = pickle.load(open('models/model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/next-page')
def next_page():
    return render_template('next-page.html')

@app.route('/third-page')
def third_page():
    return render_template('third-page.html')

@app.route('/adjust-contrast-server', methods=['POST'])
def adjust_contrast_server():
    if 'imageData' in request.files:
        image_file = request.files['imageData']
        contrast = float(request.form.get('contrast', 1.0))  # Get the contrast value from the request

        try:
            # Read the image file and decode it
            decoded_data = image_file.read()

            # Open the image using PIL
            img = Image.open(io.BytesIO(decoded_data))
            # The image data is valid, proceed with processing
            resized_image = img.resize((500, 500))  # Adjust the size as needed
            # Adjust the contrast of the image
            enhancer = ImageEnhance.Contrast(resized_image)
            adjusted_image = enhancer.enhance(contrast)

            # Convert the adjusted image back to base64 format
            buffered = io.BytesIO()
            adjusted_image.save(buffered, format='PNG')
            encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

            return encoded_image
        except Exception as e:
            print("Error processing image:", e)
            return "Error processing image"
    else:
        return "No image data received"


    
@app.route('/get-image/<path:image_name>')
def get_image(image_name):
    if 'uploaded_image' in session and image_name == 'uploaded_image':
        image_data = session['uploaded_image']
        return Response(image_data, mimetype='image/png')

    # Return a default image if the requested image is not found
    return send_from_directory('static', 'default_image.png')

@app.route('/upload-image', methods=['POST'])
def upload_image():
    image_file = request.files['image']
    image_data = image_file.read()
    session['uploaded_image'] = base64.b64encode(image_data).decode('utf-8')  # Store the base64-encoded image data in the session
    return base64.b64encode(image_data).decode('utf-8')

@app.route('/predict', methods=['POST'])
def predict():
    uploaded_image = session.get('uploaded_image')  # Retrieve the base64-encoded image data from the session
    if uploaded_image is None:
        return "No image data found."

    # Process the uploaded image with the model
    # ...

    return render_template('index.html', prediction_text='Final image prediction: ...')

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode
