import numpy as np
from flask import Flask, request, render_template, session, send_from_directory, Response, url_for, send_file
import pickle
import base64
from PIL import Image, ImageEnhance, ImageOps
import io
from flask_uploads import IMAGES, UploadSet, configure_uploads
import torch
import cv2

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

from werkzeug.utils import secure_filename

from segment.segmentAnything import better_cropped_mask, cropped_objects
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
# from lama_inpaint import inpaint_img_with_lama, build_lama_model, inpaint_img_with_builded_lama
import os
import replicate

os.environ['REPLICATE_API_TOKEN'] = 'r8_W7GHOzDckeNyNAbaCUf8ts80TY71ve31LRUT6'


app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Set a secret key for session encryption
app.config['UPLOADED_PHOTO'] = 'uploads'
app.config['UPLOADED_PHOTOS_DEST'] = './uploads'

SEGMENTS_PATH = './segmented_images/'


photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


# Load models when initializing the app
model = {}
# build the sam model
model_type="vit_h"
sam_ckpt="./pretrained_models/sam_vit_h_4b8939.pth"
model_sam = sam_model_registry[model_type](checkpoint=sam_ckpt)
print("sam_ckpt is loaded")
device = "cuda" if torch.cuda.is_available() else "cpu"
model_sam.to(device=device)
model['sam'] = SamPredictor(model_sam)
print("model_sam is loaded")
mask_generator = SamAutomaticMaskGenerator(model_sam)

class UploadForm(FlaskForm):
    photo = FileField( 
        validators= [FileAllowed(photos, 'Only images are allowed'), 
                     FileRequired('File field should not be empty')])
    submit = SubmitField('Upload')

@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTO'], filename)

@app.route('/backend-image-endpoint/<image_name>')
def serve_image(image_name):
    image_path = f'./segmented_images/{image_name}.png'
    return send_file(image_path, mimetype='image/png')

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    form = UploadForm()
    file_url = None  # Initialize file_url to None
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('get_file', filename = filename)
        session['file_url'] = file_url  # Store the file_url in the session
    else:
        session['file_url'] = None
    return render_template('index.html', form=form, file_url=session.get('file_url'))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/next-page')
def next_page():
    file_url = session.get('file_url')  # Retrieve the file_url from the session
    return render_template('next-page.html', file_url=file_url)

@app.route('/third-page')
def third_page():
    file_url = session.get('file_url')  # Retrieve the file_url from the session
    return render_template('third-page.html', file_url=file_url)

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


    
# @app.route('/get-image/<path:image_name>')
# def get_image(image_name):
#     if 'uploaded_image' in session and image_name == 'uploaded_image':
#         image_data = session['uploaded_image']
#         return Response(image_data, mimetype='image/png')

#     # Return a default image if the requested image is not found
#     return send_from_directory('static', 'default_image.png')

# @app.route('/upload-image', methods=['POST'])
# def upload_image():
#     image_file = request.files['image']
#     image_data = image_file.read()
#     session['uploaded_image'] = base64.b64encode(image_data).decode('utf-8')  # Store the base64-encoded image data in the session
#     return base64.b64encode(image_data).decode('utf-8')

@app.route('/predict', methods=['GET'])
def predict():
    # get uploaded image 
    file_url = session.get('file_url')
    file_url_complete = '.'  + file_url
    image_file = cv2.imread(file_url_complete)
    # image_file = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if image_file is None:
        return "No image data found."
    print("finally image_file is not None")

    # resize the image
    # scale_percent = 30 # percent of original size
    # width = int(image_file.shape[1] * scale_percent / 100)
    # height = int(image_file.shape[0] * scale_percent / 100)
    # dim = (width, height)
  
    # # resize image
    # image_file = cv2.resize(image_file, dim, interpolation = cv2.INTER_AREA)
    # print(image_file.shape)

    masks = mask_generator.generate(image_file)
    print("masks are generated")

    # numMasks = len(masks) if len(masks) < 10 else 10
    # masks = masks[:numMasks]
    destination_path = './segmented_images/'
    segment_map = np.zeros((image_file.shape[0], image_file.shape[1]))
    segment_index = 0

    # for i in range(masks):
    for i in range(len(masks)):
        image_file = cv2.imread(file_url_complete)
        # image_file = cv2.resize(image_file, dim, interpolation = cv2.INTER_AREA)
        segmentname = "segment" + str(segment_index)
        # s = better_cropped_mask(masks, i, image_file)
        s = cropped_objects(masks, i, image_file, segment_map)
        if s is not False:
            cv2.imwrite(destination_path + segmentname + ".png", s)
            segment_index += 1
    

    return "segments are generated"

@app.route('/run-diffusion-model', methods=['POST'])
def run_diffusion_model():
    prompt = request.form.get('prompt')
    output = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        input={"prompt": prompt}
    )
    return output


if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode
