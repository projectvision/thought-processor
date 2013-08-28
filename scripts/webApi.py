
from bottle import default_app, route, run, post, request
from label_map import label_dict
from libshorttext.classifier import *
from scripts.classify import clean_text
import json



m = TextModel()
m.load('../libshorttext-1.0/training_data.model/') #path of the model


@route('/')
def welcome():
    return 'Welcome to Email Classifier. model loaded !'



@route('/api/14159265359/<text:re:.*>')
def classify(text):
    new_text = clean_text(text)
    label_id = predict_single_text(str(new_text),m)
    label_name = label_dict[label_id]
    result = dict(email=text,label_id=label_id,label_name=label_name)
    return result


@route('/api/71828/<text:re:.*>')
def get_data(text):
    try:
        jsonObj = json.loads(text)
        label=jsonObj["label"]
        text=jsonObj["text"]
        write_data(label,text)
        return "data received"
    except:
        return """wrong format. url should be like:<br> /api/71828/{"label":"14.0","text":"hello"}"""



@post('/api/71828')
def get_data():
    try:
        post_var = request.POST.dict
        label = post_var['label'][0]
        text = post_var['text'][0]
        write_data(label,text)
        return "data received"
    except:
        return """wrong format. """

def write_data(label,text):
        f = open('../data/additional_data','a')
        #f = open('/home/projectvision/classifier/data/additional_data','a')
        #process text before writing
        label = str(label).replace('\n',' _nl_ ')
        text = str(text).replace('\n',' _nl_ ')
        f.write(label+"\t"+text+"\n")
        f.close()

#application = default_app()
run(host='localhost', port=8080, debug=True)
