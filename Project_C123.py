import cv2
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as plt
from sklearn.datasets import fetch_openml #Openml used as dataset
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from PIL import Image
import PIL.Image.Ops
import os, ssl, time

if(
    not os.environ.get('PYTHONHTTPSVERIFY','') and
    getattr(ssl, '_create_unverified_context', None):
    ssl._create_default_https_context = ssl._create_unverified_context
)

X = np.load('image.npz')['arr_0']
y = pd.read_csv('C122_project.csv')['labels']
print(pd.Series(y).value_counts())
classes = ['A', 'B', 'C','D', 'E','F', 'G', 'H', 'I', 'J','K', 'L', 'M','N', 'O','P', 'Q', 'R', 'S', 'T','U', 'V', 'X','Y', 'Z']
nclasses = len(classes)

samples_per_class = 5
figure = plt.figure(figsize=(nclasses*2,(1+samples_per_class*2)))

idx_cls = 0
for cls in classes:
  idxs = np.flatnonzero(y == cls)
  idxs = np.random.choice(idxs, samples_per_class, replace=False)
  i = 0
  for idx in idxs:
    plt_idx = i * nclasses + idx_cls + 1
    p = plt.subplot(samples_per_class, nclasses, plt_idx);
    p = sns.heatmap(np.array(X[idx]).reshape(22,30), cmap=plt.cm.gray, 
             xticklabels=False, yticklabels=False, cbar=False);
    p = plt.axis('off');
    i += 1
  idx_cls += 1

#training and testing data
X_train, X_test, y_train, y_test= train_test_split(X,y,random_state=9,train_size=7500,test_size=2500)

X_train_scale = X_train/255.0
X_test_scale = X_test/255.0

clf = LogisticRegression(solver='saga', multi_class='multinomial').fit(X_train_scale, y_train)

#predicting accuracy
y_pred = clf.predict(X_test_scale)
accuracy = accuracy_score(y_test,y_pred)
print(accuracy)

#Confusion Matrix
cm = pd.crosstab(y_test, y_pred, rownames=['Actual'], colnames=['Predicted'])

p = plt.figure(figsize=(10,10));
p = sns.heatmap(cm, annot=True, fmt="d", cbar=False)

#starting camera
cap = cv2.VideoCapture(0)

while(True):
    try:
        #ret is a boolean variable that returns true if the frame is available.
        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #Creating box in center
        height, width = gray.shape
        upper_left = (int(width / 2 - 56), int(height / 2 - 56))
        bottom_right = (int(width / 2 + 56), int(height / 2 + 56))
        cv2.rectangle(gray, upper_left, bottom_right, (0,255,0), 2)

        roi = gray[upper_left[1]:bottom_right[1], upper_left[0]:bottom_right[0]]

        im_pil = Image.fromarray(roi)
        image_bw = im_pil.convert('L')
        image_bw_resized = image_bw.resize((28,28), Image.ANTIALIAS)

        image_bw_resized_inverted = PIL.ImageOps.invert(image_bw_resized)
        pixel_filter = 20

        min_pixel = np.percentile(image_bw_resized_inverted, pixel_filter)
        image_bw_resized_inverted_scaled = np.clip(image_bw_resized_inverted-min_pixel, 0, 255)

        max_pixel = np.max(image_bw_resized_inverted)
        image_bw_resized_inverted_scaled = np.asarray(image_bw_resized_inverted_scaled)/max_pixel

        test_sample = np.array(image_bw_resized_inverted_scaled).reshape(1,784)
        test_pred = clf.predict(test_sample)
        print("Predicted class is: ", test_pred)

        cv2.imshow('frame',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        pass

cap.release()
cv2.destroyAllWindows()
