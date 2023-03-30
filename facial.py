# load json and create model
from __future__ import division

import os, sys
from pathlib import Path

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json, load_model
import numpy
import numpy as np
import cv2

sys.path.append(str(Path(__file__).resolve().parents[1]))
#print("str(Path(__file__).resolve().parents[1]) : ", str(Path(__file__).resolve().parents[1]))
from globalSettings import *

base_path=os.path.dirname(os.path.realpath(__file__))
#sys.path.append(base_path)

#loading VGG model
#if useVGG:
if False: #false because vgg is removed
    IMG_SIZE = 48
    model = load_model(os.path.join(base_path,"VGG16.hdf5"))
else:
    #loading the model
    json_file = open(os.path.join(base_path,'fer.json'), 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(os.path.join(base_path,"fer.h5"))

print("Loaded model from disk")

#setting image resizing parameters
WIDTH = 48
HEIGHT = 48
x=None
y=None
labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

#loading image
#full_size_image = cv2.imread("sad-face.jpg",0)
def detect_emotion(full_size_image):
    emotion = None
    gray = full_size_image
    print("Image Loaded")
    #gray=cv2.cvtColor(full_size_image,cv2.COLOR_RGB2GRAY)
    face = cv2.CascadeClassifier(os.path.join(base_path,'haarcascade_frontalface_default.xml'))
    faces = face.detectMultiScale(full_size_image, 1.3  , 10)

    #detecting faces
    for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
            cv2.normalize(cropped_img, cropped_img, alpha=0, beta=1, norm_type=cv2.NORM_L2, dtype=cv2.CV_32F)
            cv2.rectangle(full_size_image, (x, y), (x + w, y + h), (0, 255, 0), 1)
            #predicting the emotion
            if useVGG:
                #test_image = np.array(cropped_img).reshape( -1, IMG_SIZE, IMG_SIZE, 1)
                prediction = model.predict({'input_1': cropped_img })
                emotion = ''
                for i in range(0,6):
                    if(prediction[0][i] == 1):
                        emotion = labels[i]
                    
                    #print("Emotion : ", emotion)
            else:
                yhat= loaded_model.predict(cropped_img)
                #cv2.putText(full_size_image, labels[int(np.argmax(yhat))], (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_AA)
                #print("Emotion: "+labels[int(np.argmax(yhat))])
                emotion = labels[int(np.argmax(yhat))]

    #cv2.imshow('Emotion', full_size_image)
    cv2.destroyAllWindows()
    return emotion