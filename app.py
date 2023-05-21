import numpy as np
from flask import Flask, request, render_template, session
import pickle

app = Flask(__name__)
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

@app.route('/upload-image', methods=['POST'])
def upload_image():
    image_file = request.files['image']
    image_data = image_file.read()
    session['uploaded_image'] = image_data  # Store the image data in the session
    return "Image uploaded successfully!"

@app.route('/predict', methods=['POST'])
def predict():
    uploaded_image = session.get('uploaded_image')  # Retrieve the image data from the session
    if uploaded_image is None:
        return "No image data found."

    # Process the uploaded image with the model
    # ...

    return render_template('index.html', prediction_text='Final image prediction: ...')

if __name__ == '__main__':
    app.run()
