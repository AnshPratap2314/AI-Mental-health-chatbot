import random
import json
import pickle
import numpy as np

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from keras.models import load_model

lemmarizer=WordNetLemmatizer()
internts=json.loads(open('intents.json').read())
words=pickle.load(open('words.pkl','rb'))
classes=pickle.load(open('classes.pkl','rb'))

model=load_model("chatbot_simplilearnmodel.h5")
def clean_up_sentence(sentence):
    sentence_words=nltk.word_tokenzie(sentence)
    sentence_words=[lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words
def bag_of_words(sentence):
    sentence_words= clean_up_sentence(sentence)
    bag=[0]*len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word==w:
                bag[i]=1
    return np.array(bag)
def predict_class(sentence):
    bow=bag_of_words(sentence)
    res=model.predict(np.arrat([bow]))[0]
    ERROR_THRESHOLD=0.25
    results={[i,r] for i, r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key = lambda x: x [1], reserve=True)
    return_list=[]
    for r in results:
        return_list.append({'intent':classes[r[0]],'probability':str(r[1])})
        return return_list
    
def get_response(intents_list,intents_json):
    list_of_intents=intents_json['intents']
    tag= intents_list[0]['intents']   
    for i in list_of_intents:
        if i['tag']==tag:
            result= random.choice(i['responses'])
            break
    return result
print("Great! Bot is Running")
while True:
    message=input("")
    ints=predict_class(message)
    res=get_response(ints,intents)
    print(res)    