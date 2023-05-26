# app.py
from flask import Flask, flash, request, redirect, jsonify, send_file
from werkzeug.utils import secure_filename
import patch_match
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'files/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    image = request.files['image']
    mask = request.files['mask']
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
        print('upload_image filename: ' + image_name)
        print('upload_image filename: ' + mask_name)

        img = Image.open('files/' + image_name)
        msk = Image.open('files/' + mask_name)
        result = patch_match.inpaint(img, msk, patch_size=1)
        output = Image.fromarray(result, 'RGB')
        output.save('files/output.jpg')

        os.remove('files/' + image_name)
        os.remove('files/' + mask_name)

        return send_file(os.path.join('files', 'output.jpg'), mimetype='image/jpeg')


# @app.route('/output', methods=['GET'])
# def show_image():
#     return send_file(os.path.join('static/uploads', 'output.jpg'), mimetype='image/jpeg')


if __name__ == "__main__":
    app.run()
