import os
import cv2
import datetime
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
import pydicom
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import StringIO

from detect_new import run

app = Flask(__name__)
app.secret_key = 'seacret_key'
#ALLOWED_EXTENSIONS = set(['dcm'])


@app.route('/')
def index():
    return render_template("index.html")




@app.route('/post', methods=['POST'])
def post():
    img_dir = "static/imgs/"
    dcm_dir = "static/dcms/"
    memo_dir = "static/memo/"
    # dcmの保存
    file = request.files["input_img"]
    session["dt_now"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    session["yolo"] = True
    dcm_path = dcm_dir + session["dt_now"] + ".dcm"
    file.save(dcm_path)
    # jpgへの変換
    dicom = pydicom.read_file(dcm_path)
    data = dicom.pixel_array
    data = data - np.min(data)
    if np.max(data) != 0:
        data = data / np.max(data)
    img = (data * 255).astype(np.uint8)
    session["img_path"] = img_dir + session["dt_now"] + ".jpg"
    cv2.imwrite(session["img_path"], img)
    # テキストデータの保存
    text_path = memo_dir + session["dt_now"] + ".txt"
    session["title"] = request.form["input_title"]
    session["memo"] = request.form["input_memo"]
    f = open(text_path, 'w')
    f.write(session["title"])
    f.write("\n")
    f.write(session["memo"])
    f.close()
    return redirect(url_for('testviewer'))

@app.route('/testviewer')
def testviewer():
    if "dt_now" not in session:
        return redirect(url_for('index'))

    if session["yolo"]:
        class opt:
            weights = "./runs/train/exp13/weights/best.pt"
            source = session["img_path"]
            img_size = 512
            conf_thres = 0.2
            iou_thres = 0.4
            device = ''
            view_img = False
            save_txt = True
            save_conf = True
            classes = None
            agnostic_nms = False
            augment = False
            update = False
            project = 'static/imgs/detect'
            name = 'exp'
            exist_ok = False
        save_dir = run(opt)
        save_dir = os.path.join(save_dir, session["dt_now"]+".jpg")
        session["img_path"] = save_dir

    return render_template("testviewer.html", dt_now=session["dt_now"], output_title=session["title"], output_memo=session["memo"], img_path=session["img_path"])

@app.route('/viewer')
def viewer():
    dcm_dir = "static/dcms/"
    dicom_path = dcm_dir + "test.dcm"
    return render_template("viewer.html", dicom_path=dicom_path)

@app.route('/results')
def results():
    return render_template("results.html")

if __name__ == "__main__":
    app.run(debug=True)