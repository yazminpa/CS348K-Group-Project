import numpy as np
from flask import Flask, request, render_template, session, send_from_directory, Response, url_for
import pickle
# import torch
import base64
from PIL import Image, ImageEnhance, ImageOps
import io
from flask_uploads import IMAGES, UploadSet, configure_uploads


from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
# from segment.segmentAnything import better_cropped_mask
# from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
# # from lama_inpaint import inpaint_img_with_lama, build_lama_model, inpaint_img_with_builded_lama
# from utils.utils import load_img_to_array, load_base64_to_array, load_array_to_base64

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'your_secret_key'  # Set a secret key for session encryption
app.config['UPLOADED_PHOTO'] = 'uploads'
app.config['UPLOADED_PHOTOS_DEST'] = '/Users/yazminpadilla/CS348K-Group-Project/uploads'


photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class UploadForm(FlaskForm):
    photo = FileField( 
        validators= [FileAllowed(photos, 'Only images are allowed'), 
                     FileRequired('File field should not be empty')])
    submit = SubmitField('Upload')

@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTO'], filename)

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




# model = pickle.load(open('models/model.pkl', 'rb'))

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
    uploaded_image_base64 = session.get('uploaded_image')  # Retrieve the base64-encoded image data from the session
    if uploaded_image_base64 is None:
        return "No image data found."
    
    # Process the uploaded image with the model
    # image_array = load_base64_to_array(uploaded_image_base64)
    image_file = request.files['imageData']
    print(image_file)
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
        segmentname = "segment" + str(i)
        session[segmentname] = load_array_to_base64(better_cropped_mask(masks, i, image_array)) 
        # segments.append(better_cropped_mask(masks, i, image_array))

    # segments : the top ten objects in the image-> should be displayed in the next page 

    return render_template('index.html', prediction_text='Final image prediction: ...')

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode
