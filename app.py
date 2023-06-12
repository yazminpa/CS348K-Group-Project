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
from flask import Flask, request, jsonify

import openai
import requests


os.environ['REPLICATE_API_TOKEN'] = 'r8_U7fxcLt6Vd17mFdkLX4SAnvVimxb8Cn2drpdj'#'r8_W7GHOzDckeNyNAbaCUf8ts80TY71ve31LRUT6'


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

# @app.route('/forth-page')
# def forth_page():
#     file_url = session.get('file_url')  # Retrieve the file_url from the session
#     return render_template('forth-page.html', file_url=file_url)

def apply_style_changes(image, grayscale=False, saturation=None, brightness=None, hue_rotate=None):
    # Convert the image to grayscale if requested
    if grayscale:
        image = ImageOps.grayscale(image)

    # Adjust image saturation if a value is provided
    if saturation is not None:
        saturation = (float(saturation) - 100.0) / 100.0  # Convert to float and scale to the range [-1, 1]
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.0 + saturation)

    # Adjust image brightness if a value is provided
    if brightness is not None:
        brightness = (float(brightness) - 100.0) / 100.0  # Convert to float and scale to the range [-1, 1]
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.0 + brightness)

    # Adjust image hue if a value is provided
    if hue_rotate is not None:
        hue_rotate = float(hue_rotate) * 360.0 / 300.0  # Convert to float and scale to the range [0, 360]
        image = image.convert('RGB')
        image = image.convert('HSV')
        h, s, v = image.split()
        np_h = np.array(h)
        np_h = (np_h + hue_rotate) % 256
        h = Image.fromarray(np_h.astype('uint8'), mode='L')
        image = Image.merge('HSV', (h, s, v))
        image = image.convert('RGB')
        
    return image
@app.route('/save-images', methods=['POST'])
def save_images():
    vector_data = request.json.get('vector')  # Retrieve the vector data from the request
    print("Received vector data:")
    print("len of vector", len(vector_data))
    # Check if vector_data is not empty
    if vector_data:
        # Create the directory if it doesn't exist
        if not os.path.exists('./edited_images'):
            os.makedirs('./edited_images')

        # Check if the vector_data contains at least one image object
        if isinstance(vector_data, list) and len(vector_data) > 0:
            # Iterate over each image object in the vector data
            for index, image_object in enumerate(vector_data):
                if isinstance(image_object, dict):
                    # Retrieve the image data and style change parameters from the image object
                    image_data = image_object.get('data')
                    grayscale = image_object.get('grayscale')
                    saturation = image_object.get('saturation')
                    brightness = image_object.get('brightness')
                    hue_rotate = image_object.get('hueRotate')

                    # Check if all required parameters are present
                    if image_data is not None and grayscale is not None and saturation is not None and brightness is not None and hue_rotate is not None:
                        # Remove the prefix "data:image/png;base64," from the image data
                        image_data = image_data.replace('data:image/png;base64,', '')

                        # Decode the base64 image data and convert it to bytes
                        image_bytes = base64.b64decode(image_data)

                        # Create a PIL image object from the image data
                        image = Image.open(io.BytesIO(image_bytes))

                        # Apply style changes
                        image = apply_style_changes(image, grayscale=grayscale, saturation=saturation, brightness=brightness, hue_rotate=hue_rotate)

                        # Save the image to the server
                        image_name = f'image_{index}.png'
                        image_path = os.path.join('./edited_images', image_name)
                        image.save(image_path)
                    else:
                        print("Missing parameters for image object:")
                else:
                    print("Invalid image object:")
        else:
            print("Invalid vector data: vector_data should be a non-empty list")
            return jsonify({'success': False, 'message': 'Invalid vector data'})

        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/forth-page')
def forth_page():
    output_image_url = session.get('output_image_url')  # Retrieve the output image URL from the session
    return render_template('forth-page.html', image_url=output_image_url)


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
            img, tmask = s
            cv2.imwrite( destination_path + segmentname + ".png", img)
            cv2.imwrite( destination_path + segmentname + "_tmask.png", tmask)        
            segment_index += 1
    

    return "segments are generated"

@app.route('/dalle_edit', methods=['GET'])
def edit_dalle():

    # openai setting
    openai.api_key = os.getenv("OPENAI_API_KEY")
    image_path = "path/to/image.png"
    mask_path = "path/to/mask.png"
    prompt = ""
    response = openai.Image.create_edit(
                                image=open(image_path, "rb"),
                                mask=open(mask_path, "rb"),
                                prompt=prompt,
                                n=1,
                                size="256x256"
                                )
    image_url = response['data'][0]['url']
    # TODO: get the image in image_url and save it to backend


    return "dalle edit is done"


@app.route('/combine', methods=['GET'])
def combine(selected_segments):
    # TODO: get the selected segments from frontend
    return "combine is done"

@app.route('/run-diffusion-model', methods=['POST'])
def run_diffusion_model():
    prompt = request.get_json().get('prompt')
    if not prompt:
        return jsonify({'error': 'Missing prompt'}), 400

    output = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        input={"prompt": prompt}
    )
    session['output_image_url'] = output[0]
    print(output[0])

    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode
