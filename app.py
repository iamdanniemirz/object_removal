import serverless_wsgi
from flask import Flask, flash, request, redirect, jsonify, send_file, make_response
import os
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import patch_match

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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


@app.route('/', methods=['POST'])
def hello_world():
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

        img = Image.open('/tmp/' + image_name)
        img = convert_image(img)
        msk = Image.open('/tmp/' + mask_name)
        msk = convert_mask(msk)

        result = patch_match.inpaint(img, msk, patch_size=int(ps))
        output = Image.fromarray(result, 'RGB')
        output.save('/tmp/output.jpg')

        os.remove('/tmp/' + image_name)
        os.remove('/tmp/' + mask_name)

        return send_file(os.path.join('/tmp', 'output.jpg'), mimetype='image/jpeg')


def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)


# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(debug=True, host='0.0.0.0', port=port)
