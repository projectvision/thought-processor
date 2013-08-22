
from bottle import default_app, route, run
from label_map import label_dict
from libshorttext.classifier import *
from scripts.classify import clean_text



m = TextModel()
m.load('../libshorttext-1.0/libshort_data.model') #path of the model


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


#application = default_app()
run(host='localhost', port=8080, debug=True)
