# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 15:25:43 2021

"""
# pip install imutils
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from tensorflow.keras.optimizers import SGD
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np

#########################ImageToArrayPreprocessor##############################
# imports the img_to_array function from Keras
from keras.preprocessing.image import img_to_array


class ImageToArrayPreprocessor:
    def __init__(self, dataFormat=None):
        # store the image data format
        self.dataFormat = dataFormat

    def preprocess(self, image):
        # apply the the Keras utility function that correctly rearranges
        # the dimensions of the image
        return img_to_array(image, data_format=self.dataFormat)


########################SimplePreprocessor####################################
import cv2


class SimplePreprocessor:
    def __init__(self, width, height, inter=cv2.INTER_AREA):
        # store the target image width, height, and interpolation
        # method used when resizing
        self.width = width
        self.height = height
        self.inter = inter

    def preprocess(self, image):
        # resize the image to a fixed size, ignoring the aspect
        # ratio
        return cv2.resize(image, (self.width, self.height),
                          interpolation=self.inter)


########################SimpleDatasetLoader###################################
# import numpy as np
# import cv2
import os


class SimpleDatasetLoader:
    def __init__(self, preprocessors=None):
        # store the image preprocessor
        self.preprocessors = preprocessors

        # if the preprocessors are None, initialize them as an
        # empty list
        if self.preprocessors is None:
            self.preprocessors = []

    def load(self, imagePaths, verbose=-1):
        # initialize the list of features and labels
        data = []
        labels = []

        # loop over the input images
        for (i, imagePath) in enumerate(imagePaths):
            # load the image and extract the class label assuming
            # that our path has the following format:
            # /path/to/dataset/{class}/{image}.jpg
            image = cv2.imread(imagePath)
            label = imagePath.split(os.path.sep)[-2]

            # check to see if our preprocessors are not None
            if self.preprocessors is not None:
                # loop over the preprocessors and apply each to
                # the image
                for p in self.preprocessors:
                    image = p.preprocess(image)

            # treat our processed image as a "feature vector"
            # by updating the data list followed by the labels
            data.append(image)
            labels.append(label)

            # show an update every `verbose` images
            if verbose > 0 and i > 0 and (i + 1) % verbose == 0:
                print("[INFO] processed {}/{}".format(i + 1,
                                                      len(imagePaths)))

        # return a tuple of the data and labels
        return (np.array(data), np.array(labels))


##################################LeNet#######################################
from keras.models import Sequential
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Flatten
from keras.layers.core import Dense
from keras import backend as K


class LeNet:

    @staticmethod
    def build(width, height, depth, classes):
        model = Sequential()
        inputShape = (height, width, depth)

        if K.image_data_format() == "channels_first":
            inputShape = (depth, height, width)

        model.add(Conv2D(
            20,
            kernel_size=(5, 5),
            padding="same",
            input_shape=inputShape
        ))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(strides=(2, 2)))
        model.add(Conv2D(
            50,
            kernel_size=(5, 5),
            padding="same"
        ))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(strides=(2, 2)))
        model.add(Flatten())
        model.add(Dense(500))
        model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))

        return model


######################## Main Program ########################################
print("[INFO] loading images...")
path_to_dataset = "D:/MCUT/Neural Network/datasets/animals"
imagePaths = list(paths.list_images(path_to_dataset))
sp = SimplePreprocessor(28, 28, 3)
iap = ImageToArrayPreprocessor()

sdl = SimpleDatasetLoader(preprocessors=[sp, iap])
(data, labels) = sdl.load(imagePaths, verbose=500)
# convert values to between 0-1
data = data.astype("float") / 255.0

# partition our data into training and test sets
(trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=0.25,
                                                  random_state=42)

# convert the labels from integers to vectors
trainY = LabelBinarizer().fit_transform(trainY)
testY = LabelBinarizer().fit_transform(testY)

# initialize the optimizer and model
print("[INFO] compiling model...")

# initialize stochastic gradient descent with learning rate of 0.005
# how to tune learning rates ?????
opt = SGD(lr=0.005)
# Instantiate ShallowNet architecture
# input image size 32x32
# output class is 3
model = LeNet.build(width=28, height=28, depth=3, classes=3)
model.summary()
# compile the model
# loss function: cross-entropy and optimizer: SGD
model.compile(loss="categorical_crossentropy", optimizer=opt,
              metrics=["accuracy"])
no_epochs = 100
no_verbose = 1
no_batch_size = 32  # 32 images will be presented to the network at a time,
# and a full forward and backward pass will be
# done to update the parameters of the network
# train the network
print("[INFO] training network...")

H = model.fit(trainX, trainY, validation_data=(testX, testY),
              batch_size=no_batch_size,
              epochs=no_epochs,
              verbose=no_verbose)

print("[INFO] evaluating network...")

predictions = model.predict(testX, batch_size=no_batch_size)

print(classification_report(
    testY.argmax(axis=1),
    predictions.argmax(axis=1),
    target_names=["cat", "dog", "panda"]
))

plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, no_epochs), H.history["loss"], label="train_loss")
plt.plot(np.arange(0, no_epochs), H.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, no_epochs), H.history["accuracy"], label="train_acc")
plt.plot(np.arange(0, no_epochs), H.history["val_accuracy"], label="val_acc")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend()
plt.show()

##############################################################################
