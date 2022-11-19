import re
import numpy as np
import os
from flask import Flask, url_for, render_template, request, redirect, session
import sys
from cloudant.client import db
from flask import flask , app,request,render_template
import argparse
from tensorflow import keras
from PIL import Image
from timeit import default_timer as timer
import test
import pandas as pd
import numpy as np
import random


def get_parent_dir(n=1):
    """ returns the n-th parent directory of the current
    working directory"""
    current_path = os.path.dirname(os.path.abspath(__file__))
    for k in range(n):
        current_path = os.path.dirname(current_path)
    return current_path

src_path = r'C:\Users\VIJAYARAGAVAN\OneDrive\Desktop\yolo_structure\2_Training\src'
print(src_path)
utils_path = r'C:\Users\VIJAYARAGAVAN\OneDrive\Desktop\yolo_structure\Utils'
print(utils_path)

sys.path.append(src_path)
sys.path.append(utils_path)

import argparse
from keras_yolo3.yolo import YOLO, detect_video
from PIL import Image
from timeit import default_timer as timer
from utils import load_extractor_model,load_features,parse_input,detyect_object
import test
import utils
import pandas as pd
import numpy as np
from Get_File_Paths import GetFileList
import random

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

#set up folder names for default values
data_folder = os.path.join(get_parent_dir(n=1),"Skin Disease-Flask", "Data")
image_folder = os.path.join(data_folder,"Source_Images")

image_test_folder = os.path.join(image_folder, "Test_images")

detection_results_folder = os.path.join(image_folder,"Test_Image_Detection_Results")
detection_results_file = os.path.join(detection_results_folder , "Detection_results.csv")

model_folder = os.path.join(data_folder , "Model_Weights")

model_weights = os.path.join(model_folder , "trained_weights_final.h5")
model_classes = os.path.join(model_folder, "data_classes.txt")

anchors_path = os.path.join(src_path , "keras_yolo3","model_data","yolo_anchors.txt")

FLAGS = None

app = Flask(__name__)

app.debug = True



@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('Index.html')
    else:
        return render_template('index.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('index.html', message="Incorrect Details")


@app.route('/logout', methods=['GET', 'POST'])
def res(): 
    # Delete all default flags
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)

#Command Line options

    parser.add_argument(

        "--input_path",

        type=str,

        default=image_test_folder, 
        help="Path to image/video directory. ALL subdirectories will be included. Default is "
        +image_test_folder,
    )

    parser.add_argument( 
        "--output",

        type=str,

        default=detection_results_folder, 
        help="Output path for detection results. Default is " 
        + detection_results_folder,
    )

    parser.add_argument(

        "--no_save_img",
        default=False,
        action="store_true", 
        help="Only save bounding box coordinates but do not save output imoges with annotated boxes. Default is False.",
    )
    parser.add_argument(

        "--file_types",
        " -names-List",
        nargs="*",
        default=[],
        help="Specify list of file types to include. Default is --file_types .jpg .jpeg .png .mp4",
    )
    parser.add_argument(

        "--yolo_model",

        type=str,

        dest="model_path",

        default=model_weights,

        help="Path to pre-trained weight files. Default is + model_weights",
    )
    parser.add_argument(

        "--anchors",

        type=str,

        dest="anchors_path",

        default=anchors_path,

        help="Path to YOLO anchors. Default is " + anchors_path,
    )
    parser.add_argument(

        "--classes",

        type=str,

        dest= "classes_path",

        default=model_classes,

        help="Path to YOLO class specifications. Default is "+model_classes,
    )

    parser.add_argument(

        "--confidence",

        type=float,

        dest="score",

        default=0.25,

        help="Threshold for YOLO object confidence score to show predictions. Default is 8.25.",
    )

    parser.add_argument(

        "--box_file",

        type=str,

        dest="box",

        default=detection_results_file,

        help="File to save bounding box results to. Default is "

        + detection_results_file,
    )

    parser.add_argument(

    "--postfix",

    type=str,

    dest="postfix",

    default=" disease", help="Specify the postfix for images with bounding boxes. Default is disease",

    )

    FLAGS= parser.parse_args()
    save_img = not FLAGS.no_save_img
    file_types = FLAGS.no_save_img
    #print(input_path)

    if file_types:

        input_paths =GetFileList (FLAGS.input_path, endings=file_types) 
        print(input_paths)

    else:

        input_paths =GetFileList(FLAGS. input_path)

        print(input_paths)

    # Split images and videos

    img_endings = (".jpg", ".jpeg", ".png")

    vid_endings = (".mp4", ".mpeg", ".mpg", ".avi")

    input_image_paths = []
    input_video_paths = []

    for item in input_paths:
        if item.endswith(img_endings):
            input_image_paths.append(item)
        elif item.endswith(vid_endings):
            input_video_paths.append(item)

    output_path = FLAGS.output

    if not os.path.exists(output_path): 
        os.makedirs (output_path)

    # define YOLO detector

    yolo = YOLO(
        **{
            "model_path": FLAGS.model_path,
            "anchors_path": FLAGS.anchors_path, 
            "classes_path": FLAGS.classes_path, 
            "gpu_num": FLAGS.gpu_num,
            "score": FLAGS.score,
            "model_image_size": (416, 416),
        }
    )

    # Make a dataframe for the prediction outputs 
    out_df =pd.DataFrame(

        columns=[
            "image",
            "image_path",
            "xin",
            "ymin", 
            "xmax"
            "ymax",
            "Label", 
            "confidence",
            "x_sixe",
            "y_size",
        ]
    )

    # labels to draw on images
    class_file=open (FLAGS.classes_path, "r")
    input_labels= [line.rstrip("\n") for line in class_file.readlines()] 
    print("Found () input Labels: {}".format(len(input_labels), input_labels))

    if input_image_paths:

        print(

            "Found () input images: {}".format( len(input_image_paths),

            [os.path.basename(f) for f in input_image_paths[:5]],
            )
        )
        start=timer() 
        text_out=""

        #This is for images

        for i, img_path in enumerate(input_image_paths): 
            print(img_path)
            prediction,image,lat,lon=detect_object(
                yolo,
                img_path,
                save_img=save_img,
                save_img_path=FLAGS.output,
                postfix=FLAGS.postfix,
            )
            print(lat,lon)
            y_size, x_size, _ = np.array(image).shape
            for single_prediction in prediction:
                out_df = out_df.append(
                    pd.DataFrame(
                        [
                            [
                                os.path.basename(img_path.rstrip("\n")),
                                img_path.rstrip("\n"),
                            ]
                            + single_prediction
                            + [x_size,y_size]
                        ],
                        columns=[
                            "image",
                            "image_path",
                            "xmin",
                            "ymin",
                            "xmax",
                            "ymax",
                            "label",
                            "confidence",
                            "x_size",
                            "y_size",
                            ],
                    )
                )
        end = timer()
        print(
            "Processed {} videos in {:.1f}sec".format(
                len(input_video_paths) / (end - start),
            )
        )
        out_df.to_csv(FLAGS.box , index=False)

    # this is for videos
    if input_video_paths:
        print(
            "found {} input videos: {} ...".format(
                len(input_video_paths),
                [os.path.basename(f) for f in input_video_paths[:5]],
            )
        )
        start = timer()
        for i , vid_path in enumerate(input_video_paths):
            output_path = os.path.join(
                FLAGS.output,
                os.path.basename(vid_path).replace(".",FLAGS.postfix + "."),
            )
            detect_video(yolo , vid_path,output_path=output_path)
        end = timer()
        print(
            "Processed {} videos in {:.1f}sec".format(
                len(input_video_paths), end - start
            )
        )
    # CLose the current yolo session
    yolo.close_session()
    return render template ('prediction.html')

    def logout():
        session['logged_in'] = False
        return redirect(url_for('index'))

    if(__name__ == '__main__'):
        app.run()

