import os
import cv2
import datetime
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
import pydicom
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import StringIO
import json
from detect_new import run
import glob

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
    title_dir = "static/title/"
    memo_dir = "static/memo/"
    # dcmの保存
    file = request.files["input_img"]
    session["dt_now"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    d = datetime.datetime.strptime(session["dt_now"], "%Y%m%d%H%M%S")
    session["dt_now_readable"] = d.strftime("%Y-%m-%d %H:%M:%S")
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
    # タイトルの保存
    title_path = title_dir + session["dt_now"] + ".txt"
    session["title"] = request.form["input_title"]
    f = open(title_path, 'w')
    f.write(session["title"])
    f.close()
    # メモの保存
    memo_path = memo_dir + session["dt_now"] + ".txt"
    session["memo"] = request.form["input_memo"]
    f = open(memo_path, 'w')
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
            project = 'static/detect'
            name = session["dt_now"]
            exist_ok = False
        save_dir = run(opt)
        save_dir = os.path.join(save_dir, session["dt_now"]+".jpg")
        session["anno_path"] = save_dir

    return render_template("testviewer.html", dt_now_readable=session["dt_now_readable"], output_title=session["title"], output_memo=session["memo"], img_path=session["img_path"], anno_path=session["anno_path"])


@app.route('/results')
def results():
    files = []
    dates = []
    titles = []
    memos = []
    annotations = []
    dcms = glob.glob("./static/dcms/*")
    annos = glob.glob("./static/annotation/*")
    a = 0
    num = len(dcms)
    for d in dcms:
        # files
        file = d[14:-4]
        files.append(file)
        # dates
        d = datetime.datetime.strptime(file, "%Y%m%d%H%M%S")
        d = d.strftime("%Y-%m-%d %H:%M:%S")
        dates.append(d)
        # titles
        f = "static/title/" + file + ".txt"
        f = open(f)
        title = f.read()
        titles.append(title)
        f.close()
        # memos
        f = "static/memo/" + file + ".txt"
        f = open(f)
        memo = f.read()
        memos.append(memo)
        f.close()
        # annotations
        try:
            annosa = annos[a]
            if annosa[20:-4] == file:
                annotations.append("あり")
                a += 1
            else:
                annotations.append("ー")
        except:
            annotations.append("ー")
    return render_template("results.html", files=files, num=num, dates=dates, titles=titles, memos=memos, annotations=annotations)


@app.route('/annotation')
def annotation():
    if "dt_now" not in session:
        return redirect(url_for("index"))
    return render_template("annotation.html", dt_now=session["dt_now"], output_title=session["title"], output_memo=session["memo"], img_path=session["img_path"])

@app.route("/processInfo/<string:info>", methods=["POST"])
def processInfo(info):
    pq_dir = "static/annotation/"
    pq_path = pq_dir + session["dt_now"] + ".txt"
    try:
        # メモの保存(追記)
        f = open(pq_path, 'a')
    except:
        # メモの保存(新規)
        f = open(pq_path, 'w')
    f.write(str(info)+"\n")
    f.close()
    return info

@app.route('/done')
def done():
    return render_template("done.html")


if __name__ == "__main__":
    app.run(debug=True)