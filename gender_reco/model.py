from PIL import Image
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from tensorflow.keras import optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
import pandas as pd
import numpy as np
import os

def create_dataset():
    '''From pictures directory creating '''    
    images = []
    genders = []
    # Would need to be a different folder
    for i in os.listdir('/content/drive/MyDrive/Colab Notebooks/data/crop_part1.zip (Unzipped Files)/crop_part1/')[0:8000]:   # Needs to put the right folder
        split = i.split('_')
        genders.append(int(split[1]))
        # Would need to be a different folder
        images.append(Image.open('/content/drive/MyDrive/Colab Notebooks/data/crop_part1.zip (Unzipped Files)/crop_part1/' + i))
    images = pd.Series(list(images), name = 'Images')
    genders = pd.Series(list(genders), name = 'Genders')
    df = pd.concat([images, genders], axis=1)
    df=df[df['Genders']!=3]
    x = []
    y = []
    for i in range(len(df)):
        df['Images'].iloc[i] = df['Images'].iloc[i].resize((200,200), Image.ANTIALIAS)
        ar = np.asarray(df['Images'].iloc[i])
        x.append(ar)
        agegen = [int(df['Genders'].iloc[i])]
        y.append(agegen)
    x = np.array(x)
    y_gender = df['Genders']
    x_train_gender, x_test_gender, y_train_gender, y_test_gender = train_test_split(x, y_gender, test_size=0.2, stratify=y_gender)
    return x_train_gender, x_test_gender, y_train_gender, y_test_gender

def create_model():
    '''Creating the convolution deep learning model'''
    genmodel = Sequential()
    genmodel.add(Conv2D(32, (3,3), activation='relu', input_shape=(200, 200, 3)))
    genmodel.add(MaxPooling2D((2,2)))
    genmodel.add(Conv2D(64, (3,3), activation='relu'))
    genmodel.add(MaxPooling2D((2,2)))
    genmodel.add(Conv2D(128, (3,3), activation='relu'))
    genmodel.add(MaxPooling2D((2,2)))
    genmodel.add(Flatten())
    genmodel.add(Dense(64, activation='relu'))
    genmodel.add(Dropout(0.5))
    genmodel.add(Dense(1, activation='sigmoid'))
    genmodel.compile(loss='binary_crossentropy',
                optimizer=optimizers.Adam(learning_rate=0.0001),
                metrics=['accuracy'])
    return genmodel

def run_model(genmodel,x_train_gender, x_test_gender, y_train_gender, y_test_gender):
    datagen = ImageDataGenerator(
        rescale=1./255., width_shift_range = 0.1, height_shift_range = 0.1, horizontal_flip = True)
    test_datagen = ImageDataGenerator(rescale=1./255)
    train2 = datagen.flow(x_train_gender, y_train_gender, batch_size=64)
    test2 = test_datagen.flow(
            x_test_gender, y_test_gender,
            batch_size=64)
    es = EarlyStopping(patience = 20, restore_best_weights=True)
    history = genmodel.fit(train2, validation_data=test2,
            epochs=200,
            batch_size=16, 
            verbose=1,
            callbacks = [es])
    history.save_weights('my_model.h5') 
    return test2

def evaluate_model(genmodel, test2):
    genmodel.load_weights("../raw_data/my_model.h5")
    # genmodel.evaluate(x_test_gender, y_test_gender)    
    return genmodel.evaluate(test2)