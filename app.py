from flask import Flask, flash, request, redirect, jsonify, send_file
from werkzeug.utils import secure_filename
import patch_match
from PIL import Image
import os
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'files/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image(image):
    image = np.asarray(image)
    image = image[:, :, :3]
    out = Image.fromarray(image, 'RGB')
    return out

def convert_mask(image):
    out = image.convert('L')
    return out


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    image = request.files['image']
    mask = request.files['mask']
    ps = request.form['ps']
    if image.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if mask.filename == '':
        flash('No mask selected for uploading')
        return redirect(request.url)

    if image and allowed_file(image.filename) and mask and allowed_file(mask.filename):
        image_name = secure_filename(image.filename)
        mask_name = secure_filename(mask.filename)

        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
        mask.save(os.path.join(app.config['UPLOAD_FOLDER'], mask_name))

        img = Image.open('files/' + image_name)
        img = convert_image(img)
        msk = Image.open('files/' + mask_name)
        msk = convert_mask(msk)
        result = patch_match.inpaint(img, msk, patch_size=int(ps))
        output = Image.fromarray(result, 'RGB')
        output.save('files/output.jpg')

        os.remove('files/' + image_name)
        os.remove('files/' + mask_name)

        return send_file(os.path.join('files', 'output.jpg'), mimetype='image/jpeg')


@app.route('/string', methods=['GET', 'POST'])
def print():
    text = request.form['name']
    return text


if __name__ == "__main__":
    app.run()
