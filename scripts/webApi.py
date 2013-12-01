
from bottle import default_app, route, run, post, request
from shorttextclassifier.libshorttext.classifier import *
from scripts.classify import clean_text
from scripts.label_map import label_dict, sub_label_dict
import csv
import json
import time


m=None
def load_model(model_file):
    global m
    m = TextModel()
    m.load(model_file) #path of the model


def write_to_csv(data,csv_file):
    with open(csv_file,'a') as f:
        csv_obj = csv.writer(f)
        csv_obj.writerow(data)
        
@route('/')
def welcome():
    return 'Welcome to Email Classifier. model loaded !'

@post('/api/classify/49917331096')
def classify():
    post_var = request.POST.dict
    email_from = post_var['from'][0] 
    email_subject = post_var['subject'][0]
    email_body = post_var['body'][0]
    new_text = clean_text(email_body)
    print new_text
    label_id = predict_single_text(str(new_text),m)
    label_name = label_dict[label_id]
    sub_label_id = 0
    suggestions = sub_label_dict[label_id][sub_label_id].split(',')
    if len(suggestions) == 0:
        suggestions = ['No Action Needed']
    id = time.time()
    data = [id,email_from,email_subject,email_body,label_id,sub_label_id]
    write_to_csv(data,email_log_file)
    result = dict(email_id=id,label_id=label_id,label_name=label_name,suggestions=suggestions,sub_label_id=sub_label_id)
    return result


@post('/api/feedback/49917331096')
def get_feedback():
    try:
        post_var = request.POST.dict
        email_id = post_var['email_id'][0] 
        feedback = post_var['feedback'][0]
        data = [email_id,feedback] 
        write_to_csv(data,feedback_log_file)
        return {'status':1}
    except:
        return {'status':0}
    
@post('/api/71828')
def get_data():
    '''
    api to write extra additional_labeled emails
    '''
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


#main begins
env="local"
env="server"
email_log_file = None
feedback_log_file = None

if env == "local":
    email_log_file =  "../data/emails_table.csv"
    feedback_log_file = "../data/feedback_table.csv"
    load_model("../models/training_data.model")
    run(host="localhost", port=8080, debug=True)
    
elif env == "server":
    email_log_file =  "/home/projectvision/thought-processor/data/emails_table.csv"
    feedback_log_file = "/home/projectvision/thought-processor/data/feedback_table.csv"
    load_model("/home/projectvision/thought-processor/models/all_data.model")
    application = default_app()
    