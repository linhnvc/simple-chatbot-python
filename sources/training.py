import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import json

import numpy as np
import tflearn
import tensorflow as tf
import random

a = "="
print(a*100 + "\nChatbot by LinhNVC \nCopyright 2019")
print(tf.__version__)


with open('intents.json') as json_data:
    intents = json.load(json_data)
# print(intents)


words = []
classes = []
documents = []
stop_words = ['?', 'a', 'an', 'the']

i=1
for intent in intents['intents']:
    p=1
    for pattern in intent['patterns']:
        print("intent "+str(i), "pattern "+str(p))
        w = nltk.word_tokenize(pattern)
        # print(w)
        words.extend(w)
        # print(words)
        documents.append((w, intent['tag']))
        # print(documents)
        if intent['tag'] not in classes:
            classes.append(intent['tag'])
        p+=1
    i+=1

# print(len(words))
words = [stemmer.stem(w.lower()) for w in words if w not in stop_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))








# create our training data
training = []
output = []
output_empty = [0] * len(classes)

# training set, bag of words for each sentence
for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]

    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # output is a '0' for each tag and '1' for current tag
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])
random.shuffle(training)
training = np.array(training)

# create train and test lists
train_x = list(training[:,0])
train_y = list(training[:,1])

# print(train_x); print(train_y)

tf.reset_default_graph()
# Build neural network
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy')

# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
# Start training
# model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
# model.save('model.tflearn')

# import pickle
# pickle.dump( {'words':words, 'classes':classes, 'train_x':train_x, 'train_y':train_y}, open( "training_data", "wb" ) )










# restore our data structures
import pickle
data = pickle.load( open( "training_data", "rb" ) )
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# import intents file
import json
with open('intents.json') as json_data:
    intents = json.load(json_data)

model.load('./model.tflearn')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# bag of words
def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))


print(bow('I want to special food', words))



# data structure to hold user context
context = {}

ERROR_THRESHOLD = 0.25
def classify(sentence):
    results = model.predict([bow(sentence, words)])[0]
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    return return_list

def response(sentence, userID='1', show_details=False):
    results = classify(sentence)
    if results:
        while results:
            for i in intents['intents']:
                if i['tag'] == results[0][0]:
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        return print(random.choice(i['responses']))

            results.pop(0)


print("Predict ================ ")
print(response('when i can buy'))