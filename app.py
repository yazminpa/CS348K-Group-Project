import numpy as np
from flask import Flask, request, render_template, session, send_from_directory, Response
import pickle
import torch
import base64
from segment.segmentAnything import better_cropped_mask
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
# from lama_inpaint import inpaint_img_with_lama, build_lama_model, inpaint_img_with_builded_lama
from utils.utils import load_img_to_array, load_base64_to_array

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
    uploaded_image_base64 = session.get('uploaded_image')  # Retrieve the base64-encoded image data from the session
    if uploaded_image_base64 is None:
        return "No image data found."
    
    # Process the uploaded image with the model
    image_array = load_base64_to_array(uploaded_image_base64)

    # segement the image and get the top ten objects 
    # Load models
    model = {}
    # build the sam model
    model_type="vit_h"
    sam_ckpt="./pretrained_models/sam_vit_h_4b8939.pth"
    model_sam = sam_model_registry[model_type](checkpoint=sam_ckpt)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_sam.to(device=device)
    model['sam'] = SamPredictor(model_sam)

    mask_generator = SamAutomaticMaskGenerator(model_sam)
    masks = mask_generator.generate(image_array)

    numMasks = len(masks) if len(masks) < 10 else 10
    segments = []

    for i in range(numMasks):
        segments.append(better_cropped_mask(masks, i, image_array))

    # segments : the top ten objects in the image-> should be displayed in the next page 

    return render_template('index.html', prediction_text='Final image prediction: ...')

if __name__ == '__main__':
    app.run()
