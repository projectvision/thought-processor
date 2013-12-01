
from bottle import default_app, route, run, post, request
from libshorttext.classifier import *
from scripts.classify import clean_text
from scripts.label_map import label_dict, sub_label_dict
import MySQLdb as mdb
import csv
import json
import time

#env="local"
env="server"


email_log_file = None
feedback_log_file = None

m=None
def load_model(model_file):
    global m
    m = TextModel()
    m.load(model_file) #path of the model

conx=None
def connect_to_db(host,uname,passwd="sql",db="projectvision$default"):
    global conx
    try:
        conx = mdb.connect(host, uname,passwd, db);
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])   

def write_to_db(email_from,email_subject,email_body,label_id,sub_label_id):
    '''
    TODO: make sure that there is no conflict while getting id
    '''
    sql = "insert into emails(email_from,email_subject,email_body,label_id,sub_label_id) "
    sql += """values ("%s","%s","%s",%s,%s)""" % (email_from,email_subject,email_body,label_id,sub_label_id)
    if not conx.open:
        connect_to_db("mysql.server","projectvision","sql")
    cur = conx.cursor()
    cur.execute(sql)
    cur.close()
    id = conx.insert_id()
    conx.commit()
    return id
    

def write_to_csv(data,csv_file):
    with open(csv_file,'a') as f:
        csv_obj = csv.writer(f)
        csv_obj.writerow(data)
        
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


@post('/api/classify/49917331096')
def classify():
    post_var = request.POST.dict
    email_from = post_var['from'][0] 
    email_subject = post_var['subject'][0]
    email_body = post_var['body'][0]
    new_text = clean_text(email_body)
    label_id = predict_single_text(str(new_text),m)
    label_name = label_dict[label_id]
    sub_label_id = 0
    suggestions = sub_label_dict[label_id][sub_label_id].split(',')
    if len(suggestions) == 0:
        suggestions = ['No Action Needed']
    #id=write_to_db(email_from,email_subject,email_body,int(float(label_id)),sub_label_id)
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
    
@route('/api/71828/<text:re:.*>')
def get_data(text):
    '''
    TODO: obsolete api. to be removed
    '''
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
    '''
    TODO: obsolete api. to be removed
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
if env == "local":
    email_log_file =  "../data/emails_table.csv"
    feedback_log_file = "../data/feedback_table.csv"
    load_model("../libshorttext-1.0/training_data.model")
    #connect_to_db("localhost","root","sql")
    run(host="localhost", port=8080, debug=True)
elif env == "server":
    email_log_file =  "/home/projectvision/classifier/data/emails_table.csv"
    feedback_log_file = "/home/projectvision/classifier/data/feedback_table.csv"
    load_model("/home/projectvision/classifier/model")
    #connect_to_db("mysql.server","projectvision","sql")
    application = default_app()
