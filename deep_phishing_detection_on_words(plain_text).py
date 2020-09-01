# -*- coding: utf-8 -*-
"""Copy_of_Deep_phishing_detection_On_words(plain_text).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15ElbGKlnu9XO0RwJMcuv8O1TqwJ6hF-I
"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
!pip3 install keras sklearn tqdm numpy keras_metrics scikit-plot

"""Honors project looking into Deep learnirng detecting phishing emails 
compared four different netwkrs trained form a custom corpus with legitmate and illigitmate phishing emails in.
"""

from keras.callbacks import History 
history = History()

from keras.models import Sequential
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, LSTM, Dropout, Dense
from keras.utils import to_categorical
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.callbacks import EarlyStopping
from keras.models import Model
from keras.optimizers import RMSprop
from keras.preprocessing.text import Tokenizer
from keras.layers import Dense, Dropout, Activation,Bidirectional
from keras.layers import Embedding
from keras.layers import Conv1D, GlobalMaxPooling1D
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from sklearn.preprocessing import LabelEncoder

from keras import backend
from keras.layers import Dense
from keras import Sequential
from keras.utils import  plot_model
import numpy as np
import tqdm
import time
import sklearn.metrics as metrics
from matplotlib.pyplot import *
from matplotlib import pyplot as plt
#import keras_metrics

!pip install keras-metrics

import keras_metrics

from tensorflow.keras.optimizers import SGD
import matplotlib.pyplot as plt
from keras.utils.vis_utils import plot_model
from keras.models import model_from_json
from matplotlib.pyplot import *
from matplotlib import pyplot as plt

SEQUENCE_LENGTH = 100
EMBEDDING_SIZE = 300 #dimensions for embedding file 
TEST_SIZE = 0.5 #size of data_set
FILTERS = 70
BATCH_SIZE = 200

EPOCHS =100  # number of epochs
# give lables a numeric value
label2int = {"ham": 0, "spam": 1}
int2label = {0: "ham", 1: "spam"}

max_features = 5000
maxlen = 100
embedding_dims = 50
filters = 250
kernel_size = 7
hidden_dims = 250
pool_size = 15
lstm_output_size = 1028

def Load_data():
  text, labels = [], []
  with open("datatest2",encoding='utf-8-sig') as f: #loads dataset python 3, encodinf stig stops dataset breaking 
    for line in f:
      split = line.split()
      labels.append(split[0].strip())
      text.append(''.join(split[1:]).strip())
  return text,labels

X, y = Load_data() # loads the x and Y data

tokenizer = Tokenizer() #converts the utf-8 into tokinized characters 
tokenizer.fit_on_texts(X)
# tokinize into ints 
X = tokenizer.texts_to_sequences(X)

X = np.array(X)
y = np.array(y)
X = pad_sequences(X, maxlen=SEQUENCE_LENGTH)

y = [ label2int[label] for label in y ] #loads lables 
y = to_categorical(y)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=43) #splits the data into test and train sets

"""Loads glve embedding file"""

def get_embedding_vectors(tokenizer, dim=EMBEDDING_SIZE): #dim is dimensions EMBEDDINGSIZE is size for the netwokr and the file
    embedding_index = {}
    with open("glove.6B.300d.txt", 'r',encoding='utf8',errors = 'ignore') as f: #ignore erros is due to sometimes when reading it fails to convert values 
        for line in tqdm.tqdm(f, "Reading GloVe"):
            values = line.split()
            word = values[0]
            vectors = np.asarray(values[1:], dtype='float32') 
            embedding_index[word] = vectors

    word_index = tokenizer.word_index
    embedding_matrix = np.zeros((len(word_index)+1, dim))
    for word, i in word_index.items():
        embedding_vector = embedding_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector
            
    return embedding_matrix

"""LSTM MODEL IMPLEMENTATION
Loads model rhen calls in in other function for metrics and tetsing
"""

import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.layers import Input, ConvLSTM2D, BatchNormalization, RepeatVector, Conv2D
from keras.models import Sequential, load_model
def get_model(tokenizer, lstm_units): # builds the lstm model
    embedding_matrix = get_embedding_vectors(tokenizer) # loads glove embedding 
    model = Sequential()
    model.add(Embedding(len(tokenizer.word_index)+1, 
              EMBEDDING_SIZE,
              weights=[embedding_matrix],
              trainable=False,
              input_length=SEQUENCE_LENGTH))
    model.add(LSTM(lstm_units, recurrent_dropout=0.3))
    model.add(Dropout(0.5))
    model.add(Dense(2, activation="softmax")) #p
    model.compile(optimizer="adam", loss="categorical_crossentropy",
                  metrics=["accuracy", keras_metrics.precision(), keras_metrics.recall()])
    
    model.summary()
    return model

"""Shows model params and model diogram"""

model = get_model(tokenizer=tokenizer, lstm_units=2048)  # adds LSTM unnits to the model 
from keras.utils import plot_model
plot_model(model, to_file='model.png') # prints image

model_checkpoint = ModelCheckpoint("phish{val_loss:.2f}", save_best_only=True, #calls tensorflow callbacks and creates weights for the file 
                                    verbose=1)
# for better visualization
tensorboard = TensorBoard(f"phish{time.time()}")

# print our data shapes 
print("X_train.shape:", X_train.shape)
print("X_test.shape:", X_test.shape)
print("y_train.shape:", y_train.shape)
print("y_test.shape:", y_test.shape)
# train the model
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), #history  = model (allwos the model to run then graphs and metrics to be called later)
          batch_size=BATCH_SIZE, epochs=EPOCHS,
          callbacks=[tensorboard, model_checkpoint],
          verbose=1)
model.fit

history_dict = history.history
print(history_dict.keys())
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

model.save('lstm.h5') #saves the model

"""Loads the metrics for the network"""

# get the loss and metrics
result = model.evaluate(X_test, y_test)
# extract those
loss = result[0]
accuracy = result[1]
precision = result[2]
recall = result[3]
print(f"[+] Accuracy: {accuracy*100:.2f}%") # overall accuracy of model 
print(f"[+] Precision:   {precision*100:.2f}%") # What proportion of positive identifications was actually correct? #https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall
print(f"[+] Recall:   {recall*100:.2f}%") # What proportion of actual positives was identified correctly?

F1 = 2 * (precision * recall) / (precision + recall)
print (F1)

def rnn_lstm_predict(text): #predicts sample text 
    sequence = tokenizer.texts_to_sequences([text])
    # pad the sequence
    sequence = pad_sequences(sequence, maxlen=SEQUENCE_LENGTH)
    # get the prediction
    prediction = model.predict(sequence)   
    prob =  model.predict_proba(sequence)/100*10
  
    print(prob)
    return int2label[np.argmax(prediction)]

"""sample phihing emails to test form (get seprate form the corpus)"""

print("=====================")
print ("Phish Email Test")
print("Sextaution Email")
spam_text = "I’m aware is your password. You may not know me, and you are most likely wondering why you’re getting this mail, right Overview: I installed a malware on the adult vids (sex sites) site, and there’s more, you visited this site to have fun (you know what I mean). Once you were there on the website, my malware took control of your browser. It started operating as a keylogger and remote desktop protocol which gave me access to your webcam. Immediately after that my software collected your complete contacts (you have a good taste lol…)"
print(rnn_lstm_predict(spam_text))
print("=====================")
print ("                    ")


print("=====================")
print ("Phish Email Test")
print("Are you busy Email")
spam_text1 = "Are you around? I need to pay a vendor with the blucard."
print(rnn_lstm_predict(spam_text1))
print("=====================")
print ("                    ")




print("=====================")
print ("Phish Email Test")
print("account Email")
spam_text2 = "Dear User,Someone else was trying to use your Berkeley ID to sign into iCloud via a web browser. "
print(rnn_lstm_predict(spam_text2))
print("=====================")




print("=====================")
print ("Phish Email Test")
print("account Email")
spam_text3 = "To:Hello,  Please refer to the vital info I've shared with you using Google Drive.  Click https://www.google.com/drive/docs/file0116 "
print(rnn_lstm_predict(spam_text3))
print("=====================")



print("=====================")
print ("Phish Email Test")
print(" dear customer")
spam_text4 = "Dear customer your account has been locked please login into click to see https://dkdkdkdkddkkkkd  "
print(rnn_lstm_predict(spam_text4))
print("=====================")

print("=====================")
print ("Phish Email Test")
print("hsbc Email")
spam_text5 = "Dear HSBC Bank Personal and Premier Banking Online customer! Our Maintenance Subdivision is performing a scheduled Banking On-line Service upgrade By clicking on the link below you will begin the webform of the customer's  "
print(rnn_lstm_predict(spam_text5))
print("=====================")



print("=====================")
print ("Phish Email Test")
print("hsbc Email")
spam_text6 = "Good Morning We received 2 high value CHAPS payments requests into the branch today.Please complete and sign the attached documents and return for processing.We require this information before we can release the payments to your account."
print(rnn_lstm_predict(spam_text6))
print("=====================")
print("=====================")
print ("Phish Email Test")
print("passowrd Email")
spam_text7 = "Dear User,Someone is trying to use your password please update now."
print(rnn_lstm_predict(spam_text7))
print("=====================")


spam_text8 = "Hey hows it going."
print(rnn_lstm_predict(spam_text8))
print("=====================")


spam_text8 = "Dear customer your account has been locked please login into click to see https://dkdkdkdkddkkkkd"
print(rnn_lstm_predict(spam_text8))
print("=====================")

import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt

data = {'y_Actual':    [1,1,1,1,1,0,0,0,0,0],
        'y_Predicted': [1,1,1,1,1,1,0,0,1,0]
        }

df = pd.DataFrame(data, columns=['y_Actual','y_Predicted'])
confusion_matrix = pd.crosstab(df['y_Actual'], df['y_Predicted'], rownames=['Actual'], colnames=['Predicted'])

sn.heatmap(confusion_matrix, annot=True)
plt.show()

"""BLSTM MODEL
works much like LSTM MODEL but goes both ways during training right to left then left to right
"""

def bi_boi(tokenizer,lstm_units): #loads the function and creates a BI_rnn network 
  embedding_matrix = get_embedding_vectors(tokenizer)
  model = Sequential()
  model.add(Embedding(len(tokenizer.word_index)+1,
                      EMBEDDING_SIZE,
                      weights=[embedding_matrix],
                      trainable=False,
                      input_length =SEQUENCE_LENGTH))
  model.add(Bidirectional(LSTM(64))) #creates given network
  model.add(Dropout(0.5))
  model.add(Dense(2, activation='sigmoid'))
  plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
  model.compile(optimizer="rmsprop", loss="categorical_crossentropy",
                  metrics=["accuracy", keras_metrics.precision(), keras_metrics.recall()])
  model.summary()
  return model

model_bi_boi = bi_boi(tokenizer,lstm_units=1024)  
from keras.utils import plot_model
plot_model(model_bi_boi, to_file='model_Bi_lstm.png')

import matplotlib.pyplot as plt
from keras.callbacks import History 
plot_model(model_bi_boi, to_file='model12.png')

model_checkpoint = ModelCheckpoint("phish{val_loss:.2f}", save_best_only=True,verbose=1) #creates model checkpoints was removed for someof te netwkrs as overalp happened 
# 
history = History()
tensorboard = TensorBoard(f"phish{time.time()}")
# print our data shapes
print("X_train.shape:", X_train.shape)
print("X_test.shape:", X_test.shape)
print("y_train.shape:", y_train.shape)
print("y_test.shape:", y_test.shape)
# traiaining in progress 
model_bi_boi.fit(X_train, y_train, validation_data=(X_test, y_test),
          batch_size=BATCH_SIZE, epochs=EPOCHS,
          callbacks=[tensorboard, model_checkpoint,history],
          verbose=1)

history_dict = history.history
print(history_dict.keys())
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

"""SAVE THE MODEL"""

model_bi_boi.save('bi_lstm.h5') #saves the model

# get the loss and metrics
result = model_bi_boi.evaluate(X_test, y_test)

# extract those
loss = result[0]
accuracy = result[1]
precision = result[2]
recall = result[3]

print(f"[+] Accuracy: {accuracy*100:.2f}%") # overall accuracy of model 
print(f"[+] Precision:   {precision*100:.2f}%") # What proportion of positive identifications was actually correct? #https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall
print(f"[+] Recall:   {recall*100:.2f}%") # What proportion of actual positives was identified correctly?

F1 = 2 * (precision * recall) / (precision + recall)
print (F1)

def bi_lstm_predict(text):
    sequence = tokenizer.texts_to_sequences([text])
    # pad the sequence
    sequence = pad_sequences(sequence, maxlen=SEQUENCE_LENGTH)
    # get the prediction
    prediction = model_bi_boi.predict(sequence)[0]
    prob =  model.predict_proba(sequence)[:,1]
    print (prob)
    return int2label[np.argmax(prediction)]

spam_text10 = "Good Morning We received 2 high value CHAPS payments requests into the branch today.Please complete and sign the attached documents and return for processing.We require this information before we can release the payments to your account."

print(bi_lstm_predict(spam_text10))
print("=====================")

from sklearn.metrics import confusion_matrix

"""Hybid network 
uses parts of LSTM and a CNN 
this was used to see if combining the two would learn better
"""

def seq_boi(tokenizer): #loads the function and creates a BI_rnn network 
  embedding_matrix = get_embedding_vectors(tokenizer)
  model = Sequential()
  model.add(Embedding(len(tokenizer.word_index)+1,
                      EMBEDDING_SIZE,
                      weights=[embedding_matrix],
                      trainable=False,
                      input_length =SEQUENCE_LENGTH))

  from keras.layers import Dense, Activation, Flatten
 
  model.add(Dropout(0.8))
  model.add(Conv1D(filters,
                 kernel_size,
                 padding='same',
                 activation='softmax',
                 strides=1))
  model.add(MaxPooling1D(pool_size=pool_size))
  model.add(Bidirectional(LSTM(1024))) #creates given network
  model.add(Dense(2, activation='relu'))
  model.add(Dense(2, activation='softmax'))

  plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)
  model.compile(optimizer="adam", loss="categorical_crossentropy",
                  metrics=["accuracy", keras_metrics.precision(), keras_metrics.recall()])
  model.summary()
  return model

from keras.layers import Conv1D, MaxPooling1D
model_seq_boi = seq_boi(tokenizer)  
from keras.utils import plot_model
plot_model(model_seq_boi, to_file='seq.png')

# initialize our ModelCheckpoint and TensorBoard callbacks
# model checkpoint for saving best weights
import matplotlib.pyplot as plt

plot_model(model_seq_boi, to_file='model12.png')


# for better visualization
history = History()

# print our data shapes
print("X_train.shape:", X_train.shape)
print("X_test.shape:", X_test.shape)
print("y_train.shape:", y_train.shape)
print("y_test.shape:", y_test.shape)
# traiaining in progress 
history = model_seq_boi.fit(X_train, y_train, validation_data=(X_test, y_test),
          batch_size=BATCH_SIZE, epochs=EPOCHS,verbose=0)

# get the loss and metrics
result = model_seq_boi.evaluate(X_test, y_test)

# extract those
loss = result[0]
accuracy = result[1]
precision = result[2]
recall = result[3]

print(f"[+] Accuracy: {accuracy*100:.2f}%") # overall accuracy of model 
print(f"[+] Precision:   {precision*100:.2f}%") # What proportion of positive identifications was actually correct? #https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall
print(f"[+] Recall:   {recall*100:.2f}%") # What proportion of actual positives was identified correctly?

m = tf.keras.metrics.Recall()
m.update_state([0, 1, 1, 1], [1, 0, 1, 1])
print('Final result: ', m.result().numpy())  # Final result: 0.66



p = tf.keras.metrics.Precision()
F1 = 2 * (0.6666667 * 0.6666667) / (0.6666667 + 0.6666667)
print (F1)
print('Final result: ', p.result().numpy())  # Final result: 0.66
print ("f-score")

model_bi_boi.save('Hybrid.h5') #saves the model

history_dict = history.history
print(history_dict.keys())
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

def seq_predict(text):
    sequence = tokenizer.texts_to_sequences([text])
    # pad the sequence
    sequence = pad_sequences(sequence, maxlen=SEQUENCE_LENGTH)
    # get the prediction
    prediction = model_seq_boi.predict(sequence)[0]

    return int2label[np.argmax(prediction)]

print("=====================")
print ("Phish Email Test")
print("Sextaution Email")
spam_text = "I’m aware is your password. You may not know me, and you are most likely wondering why you’re getting this mail, right Overview: I installed a malware on the adult vids (sex sites) site, and there’s more, you visited this site to have fun (you know what I mean). Once you were there on the website, my malware took control of your browser. It started operating as a keylogger and remote desktop protocol which gave me access to your webcam. Immediately after that my software collected your complete contacts (you have a good taste lol…)"
print(seq_predict(spam_text))
print("=====================")
print ("                    ")


print("=====================")
print ("Phish Email Test")
print("Sextaution Email")
spam_text1 = "Are you around? I need to pay a vendor with the blucard."
print(seq_predict(spam_text1))
print("=====================")
print ("                    ")




print("=====================")
print ("Phish Email Test")
print("account Email")
spam_text2 = "Dear User,Someone else was trying to use your Berkeley ID to sign into iCloud via a web browser. "
print(seq_predict(spam_text2))
print("=====================")




print("=====================")
print ("Phish Email Test")
print("account Email")
spam_text3 = "To:Hello,  Please refer to the vital info I've shared with you using Google Drive.  Click https://www.google.com/drive/docs/file0116 "
print(seq_predict(spam_text3))
print("=====================")




print ("Phish Email Test")
print("example")
spam_text10 = "Hey ! Have you downloaded your copy?Today, I have a top secret ebook I would like to share with you.It contains highly confidential information about the Mind and Reality: => Download Your Matrix of Mind Reality Ebook Grab it while it is still available before these secrets banned forever... "
print(seq_predict(spam_text10))
print("=====================")

"""1d cnn model"""

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.utils import to_categorical

"""Loads theembedding file"""

# load embedding as a dict
def load_embedding(filename):
	# load embedding into memory, skip first line
	file = open(filename,'r',errors='Ignore')
	lines = file.readlines()
	file.close()
	embedding = dict()
	for line in lines:
		parts = line.split()
		embedding[parts[0]] = asarray(parts[1:], dtype='float32')
	return embedding

raw_embedding = get_embedding_vectors(tokenizer)

#custom embedidng layer for Glove 
embedding_layer = Embedding(BATCH_SIZE,[embedding_dims])

def cnn_boi(tokenizer): #loads the function and creates a BI_rnn network 
  embedding_matrix = get_embedding_vectors(tokenizer)
  model = Sequential()
  model.add(Embedding(max_features,
                    embedding_dims,
                    input_length=maxlen))
  model.add(Dropout(0.2))

  model.add(Conv1D(filters,
                 kernel_size,
                 padding='valid',
                 activation='relu',
                 strides=1))
  model.add(GlobalMaxPooling1D())

  model.add(Dense(hidden_dims))
  model.add(Dropout(0.2))
  model.add(Activation('relu'))

#thinns model to sigmoid large data ---> small Box (squashed) ^_^  
  model.add(Dense(2))
  model.add(Activation('relu'))
  plot_model(model, to_file='1d_cnn.png', show_shapes=True, show_layer_names=True)
  model.compile(loss='binary_crossentropy',
                optimizer='adam',
                metrics=['accuracy'])


  return model

cnn_model = cnn_boi(tokenizer)

import matplotlib.pyplot as plt
from keras.callbacks import History 


model_checkpoint = ModelCheckpoint("phish{val_loss:.2f}", save_best_only=True,verbose=1) #creates model checkpoints was removed for someof te netwkrs as overalp happened 
# 
history = History()
tensorboard = TensorBoard(f"phish{time.time()}")
# print our data shapes
print("X_train.shape:", X_train.shape)
print("X_test.shape:", X_test.shape)
print("y_train.shape:", y_train.shape)
print("y_test.shape:", y_test.shape)
# traiaining in progress 
cnn_model.fit(X_train, y_train, validation_data=(X_test, y_test),
          batch_size=BATCH_SIZE, epochs=EPOCHS,
          callbacks=[tensorboard, model_checkpoint,history],
          verbose=1)



from matplotlib.pyplot import *
from matplotlib import pyplot as plt

history_dict = history.history
print(history_dict.keys())
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

# Plot training & validation loss values
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.show()

# get the loss and metrics
result = cnn_model.evaluate(X_test, y_test)

# extract those
loss = result[0]
accuracy = result[1]
#precision = result[2]
#recall = result[3]

print(f"[+] Accuracy: {accuracy*100:.2f}%") # overall accuracy of model 
#print(f"[+] Precision:   {precision*100:.2f}%") # What proportion of positive identifications was actually correct? #https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall
#print(f"[+] Recall:   {recall*100:.2f}%") # What proportion of actual positives was identified correctly?

m = tf.keras.metrics.Recall()
m.update_state([0, 1, 1, 1], [1, 0, 1, 1])
print('Final result: ', m.result().numpy())  # Final result: 0.66



p = tf.keras.metrics.Poisson()
p.update_state([0, 1, 1, 1], [1, 0, 1, 1])
print('Final result: ', p.result().numpy())  # Final result: 0.66

F1 = 2 * ( 4.779524 * 6666667) / (  4.779524+ 6666667)
print (F1)

def cnn_mod(text):
    sequence = tokenizer.texts_to_sequences([text])
    # pad the sequence
    sequence = pad_sequences(sequence, maxlen=SEQUENCE_LENGTH)
    # get the prediction
    prediction = cnn_model.predict(sequence)[0]
    prob =  cnn_model.predict_proba(sequence)/100*10
    print (prob)
    return int2label[np.argmax(prediction)]

cnn_model.save('cnn_model.h5') #saves the model

print("=====================")
print ("Phish Email Test")
print("Sextaution Email")
spam_text = "I’m aware is your password. You may not know me, and you are most likely wondering why you’re getting this mail, right Overview: I installed a malware on the adult vids (sex sites) site, and there’s more, you visited this site to have fun (you know what I mean). Once you were there on the website, my malware took control of your browser. It started operating as a keylogger and remote desktop protocol which gave me access to your webcam. Immediately after that my software collected your complete contacts (you have a good taste lol…)"
print(cnn_mod(spam_text))
print("=====================")
print ("                    ")


print("=====================")
print ("Phish Email Test")
print("Sextaution Email")
spam_text1 = "Are you around? I need to pay a vendor with the blucard."
print(cnn_mod(spam_text1))
print("=====================")
print ("                    ")

print("=====================")
print ("Phish Email Test")
print("Sextaution Email")
spam_text1 = "Are you around? I need to pay a vendor with the blucard."
print(cnn_mod(spam_text1))
print("=====================")
print ("                    ")



print("=====================")
print ("Phish Email Test")
print("account Email")
spam_text2 = "Dear User,Someone else was trying to use your Berkeley ID to sign into iCloud via a web browser. "
print(cnn_mod(spam_text2))
print("=====================")




print("=====================")
print ("Phish Email Test")
print("account Email")
spam_text3 = "To:Hello,  Please refer to the vital info I've shared with you using Google Drive.  Click https://www.google.com/drive/docs/file0116 "
print(cnn_mod(spam_text3))
print("=====================")



print("=====================")
print ("Phish Email Test")
print(" dear customer")
spam_text4 = "Dear customer your account has been locked please login into click to see https://dkdkdkdkddkkkkd  "
print(cnn_mod(spam_text4))
print("=====================")

print("=====================")
print ("Phish Email Test")
print("hsbc Email")
spam_text5 = "Dear HSBC Bank Personal and Premier Banking Online customer! Our Maintenance Subdivision is performing a scheduled Banking On-line Service upgrade By clicking on the link below you will begin the webform of the customer's  "
print(cnn_mod(spam_text5))
print("=====================")



print("=====================")
print ("Phish Email Test")
print("hsbc Email")
spam_text6 = "Good Morning We received 2 high value CHAPS payments requests into the branch today.Please complete and sign the attached documents and return for processing.We require this information before we can release the payments to your account."
print(cnn_mod(spam_text6))
print("=====================")
print("=====================")
print ("Phish Email Test")
print("passowrd Email")
spam_text7 = "Dear User,Someone is trying to use your password please update now."
print(cnn_mod(spam_text7))
print("=====================")

print("passowrd Email")
spam_text8 = "Hi harry how are you today?."
print(cnn_mod(spam_text8))
print("=====================")