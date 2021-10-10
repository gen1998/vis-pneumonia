import os
import cv2
import datetime
import numpy as np
from flask import Flask, render_template, request
import pydicom
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import StringIO

app = Flask(__name__)
#ALLOWED_EXTENSIONS = set(['dcm'])


@app.route('/', methods=["GET", "POST"])
def post_dicom():
    img_dir = "static/imgs/"
    dcm_dir = "static/dcms/"
    memo_dir = "static/memo/"
    if request.method == 'GET':
        text =""
        img_path = None
    elif request.method == 'POST':
        # dcmの保存
        file = request.files["input_img"]
        dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        dcm_path = dcm_dir + dt_now + ".dcm"
        file.save(dcm_path)
        # jpgへの変換
        dicom = pydicom.read_file(dcm_path)
        data = dicom.pixel_array
        data = data - np.min(data)
        if np.max(data) != 0:
            data = data / np.max(data)
        img = (data * 255).astype(np.uint8)
        img_path = img_dir + dt_now + ".jpg"
        cv2.imwrite(img_path, img)
        # テキストデータの保存
        text_path = memo_dir + dt_now + ".txt"
        text = request.form["input_text"]
        f = open(text_path, 'w')
        f.write(text)  # 何も書き込まなくてファイルは作成されました
        f.close()
    return render_template("index.html", output_text=text, img_path=img_path)


@app.route('/viewer')
def viewer():
    dcm_dir = "static/dcms/"
    dicom_path = dcm_dir + "test.dcm"
    return render_template("viewer.html", dicom_path=dicom_path)




if __name__ == "__main__":
    app.run(debug=True)