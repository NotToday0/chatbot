import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
from nltk.tokenize import WhitespaceTokenizer


import tensorflow as tf
import random
import tflearn
import json
import numpy
import pickle

with open("intents.json") as file:
    data = json.load(file)

try:
    with open("data.pickle" , "rb") as f:
        words, labels, training ,output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = WhitespaceTokenizer().tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []
    out_empty = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)


    training = numpy.array(training)
    output = numpy.array(output)
    with open("model.tflearn" , "wb") as f:
        pickle.dump((words, labels, training ,output), f)

tf.reset_default_graph()
net = tflearn.input_data(shape = [None, len(training[0])])
net = tf.contrib.layers.fully_connected(net,10)
net = tf.contrib.layers.fully_connected(net,10)
net = tf.contrib.layers.fully_connected(net, len(output[0]))
net = tflearn.activations.softmax (net)
net = tflearn.regression(net)

model = tflearn.DNN(net)
try:
    chat.py
    #model.load("model.tflearn")
except:
    model.fit(training, output, n_epoch=2000, batch_size = 10, show_metric = True)
    model.save("model.tflearn")

def bag_of_words(s,words):
    bag = [0 for _ in range(len(words))]
    s_words = WhitespaceTokenizer().tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    return numpy.array(bag)
def chat():
    print("Start talking to the bot (Type 'quit' to exit)")
    while True:
        inp = input("You : ")
        if inp.lower == "quit":
            break
        result = model.predict([bag_of_words(inp , words)])[0]
        result_index = numpy.argmax(result)
        tag = labels[result_index]

        if result[result_index] > 0.6:
            for tg in data["intents"]:
                if tg["tag"] == tag:
                    responses = tg["responses"]

            print(random.choice(responses))
        else:
            print("I am Sorry, I did not get that")

chat()
