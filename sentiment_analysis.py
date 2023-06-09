# -*- coding: utf-8 -*-
"""Sentiment_Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Pli9psRlppPNBxB9qOubhXazjoDm7-Ip

**Loading DATA**
"""

from datasets import load_dataset
import warnings 

warnings.filterwarnings('ignore')

dataset = load_dataset("rotten_tomatoes")

"""**DATA DESCRIPTION**

> The Rotten Tomatoes dataset is a collection of movie reviews and their corresponding labels (positive or negative sentiment)
"""

dataset_orginal = dataset["train"] 

dataset_val = dataset['validation']

dataset_test = dataset['test']

print(dataset_orginal.shape)

"""**TEXT PROCESSING**
<p>


*   Lowering
*   Removing stop words(most repeated words that cannot contribute to sentence in  terms of context(meaning)

No need for additional transformations which includes handling imbalanced data because the data is already well processed



"""

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk 

nltk.download('punkt')
stop_words = set(stopwords.words('english'))

def process(text):
  text['text'] = text['text'].lower()
  text['text'] = ' '.join([x for x in word_tokenize(text['text']) if x not in stop_words and len(x) > 1])
  return dict(text)

dataset_orginal = dataset_orginal.map(process).shuffle(1000)
dataset_val = dataset_val.map(process).shuffle(1000)
dataset_test = dataset_test.map(process).shuffle(1000)

"""**Tokenizationand Bert base uncased**"""

from transformers import AutoTokenizer
import numpy as np

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokenized_data = tokenizer(dataset_orginal["text"], return_tensors="np", padding=True)
tokenized_data_val = tokenizer(dataset_val["text"], return_tensors="np", padding=True)
tokenized_data_test = tokenizer(dataset_test["text"], return_tensors="np", padding=True)


tokenized_data_org = dict(tokenized_data)
tokenized_data_val = dict(tokenized_data_val)
tokenized_data_test = dict(tokenized_data_test)


labels_orginal = np.array(dataset_orginal["label"]) 
labels_val= np.array(dataset_val["label"])  
labels_test = np.array(dataset_test['label'])

"""**Training**"""

from transformers import TFAutoModelForSequenceClassification
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard,EarlyStopping

tensorboard = TensorBoard(log_dir='./logs')
early_stopping = EarlyStopping(monitor='val_loss',patience=4)


model = TFAutoModelForSequenceClassification.from_pretrained("bert-base-uncased",num_labels=2)
model.compile(optimizer=Adam(2e-5),metrics=['accuracy'],loss='binary_crossentropy')

model.fit(tokenized_data_org,labels_orginal,validation_data=(tokenized_data_val,labels_val),epochs=10,
          callbacks=[tensorboard,early_stopping])

model.save('Sent_model_Bert')

"""**Evaluation**"""

preds_logits = model.predict(tokenized_data_test)['logits']

preds = np.argmax(preds_logits,axis=1)

from sklearn.metrics import accuracy_score,confusion_matrix

train_preds = np.argmax(model.predict(tokenized_data_org)['logits'],axis=1)

val_preds = np.argmax(model.predict(tokenized_data_val)['logits'],axis=1)

print(f"Accuracy Score on Train set: {accuracy_score(train_preds,labels_orginal)}")
print(f"Accuracy Score on validation set: {accuracy_score(val_preds,labels_val)}")
print(f"Accuracy Score on Test set: {accuracy_score(preds,labels_test)}")

import seaborn as sns

sns.heatmap(confusion_matrix(preds,labels_test),annot=True,cmap='Blues')

"""    While the model's performance may not be ideal on the validation and test sets, and there are indications of overfitting, we can still consider using it depending on your specific requirements and constraints as

    the task at hand is not mission-critical and the margin of error is acceptable, so we can still utilize the model for practical purposes
"""

#end#