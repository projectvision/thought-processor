'''
author: Ankush Shah
email: ankush.shah.nitk@gmail.com
date: 21st Oct 2013
'''

from sklearn.cluster.k_means_ import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import xlrd
import numpy as np
import cPickle as pickle

reNUM = re.compile("[0-9]")

def clean_text(text):
    '''
    cleans the text by
    1.normalizing numbers
    2. removing urls
    3.removing special characters
    4.converting to lower case
    '''
    text = str(text)
    text = " ".join([ word for word in text.split()])
    #text = replace_urls(text)
    text=reNUM.sub(" ",text)
    clean_text = ""
    allowed_spec_chars = [" ", "'","-","$","\""]
    for char in text.lower():
        if char.isalpha() or char in allowed_spec_chars:
            clean_text += char
        else:
            clean_text += " "
    return clean_text

def get_clean_data(data):
    clean_data = []
    for subject,body in data:
        #cleaned_text = clean_text(subject) + clean_text(body)
        cleaned_text = clean_text(body)
        clean_data.append(cleaned_text)
    return clean_data

def print_stats(data):
    '''
    print basic statistics about the data
    '''
    for label in data.keys():
        print label, len(data[label])

def get_data(fname):
    '''
    function to read the emails from xls file
    '''
    book = xlrd.open_workbook(fname)
    data = {}
    for i_sh in range(book.nsheets-1):
        sh = book.sheet_by_index(i_sh)
        for rownum in range(1,sh.nrows): 
            row =  sh.row_values(rownum)
            fileno, subject, body, label = row[0], row[1], row[2], row[3]
            
            if label == 4.0 or label == 5.0:
                label = 5.0
            
            try:
                data[label].append((subject,body))
            except KeyError:
                data[label] = [(subject,body)]

    print "data loaded and separated by labels"
    return data

def run_kmeans(data,label,k=3,fname="../results/kmeans"):
    if len(data) < k:
        return
    vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000,stop_words='english', use_idf=True)
    clean_data = get_clean_data(data)
    X = vectorizer.fit_transform(clean_data)
    km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1)
    km.fit(X)
    print label,np.bincount(km.labels_)
    assert len(km.labels_) == len(data)
    f = open(fname+str(int(label))+".csv",'w')
    f.write("subject\tbody\tcluster_id\n")
    for i in range(len(data)):
        subject,body = data[i]
        subject  = " ".join(str(subject).split())
        body  = " ".join(str(body).split())
        cluster_id = str(km.labels_[i])
        row = data[i]
        f.write(subject+"\t"+body+"\t"+cluster_id+'\n')
    f.close()
    
    
if __name__ == "__main__":
    data = get_data(fname="../data/Emails2.xlsx")
    print_stats(data)
    for label in data.keys():
        run_kmeans(data[label],label)
