import BeautifulSoup
import json
import random
import re
import urllib
import urllib2
import xlrd


reNUM = re.compile("[0-9]")

#reference: http://daringfireball.net/2010/07/improved_regex_for_matching_urls
reURL = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

def resolveURL(url):
        try:
            u = urllib2.urlopen("http://api.unshort.me/?r="+url)
            jsonObj = json.loads(u.read())
            resolvedURL = jsonObj["resolvedURL"]
            return resolvedURL
        except urllib2.HTTPError: 
            #print "Unable to resolve " + url    
            return None
        

def getURLTitle(url):
        url = resolveURL(url)
        try:    
            soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(url))
            urlTitle = soup.title.string
            if urlTitle is not None:
                return urlTitle
            else:
                return " "
        except:
            #print "webpage title could not be found in " + url
            return " "

def replace_urls(text):
    urls = reURL.findall(text)
    #print urls
    new_text = reURL.sub(" ",text)
    for url in urls:
        title = getURLTitle(url[0])
        #print url[0]
        new_text += title
    return new_text
    

def clean_text(text):
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
    

def get_mlp_data(file='../data/Emails2.xlsx'):
    book = xlrd.open_workbook(file)
    mlp_data = []
    count_5 = 0 
    for i_sh in range(book.nsheets-1):
        
        sh = book.sheet_by_index(i_sh)
        for rownum in range(1,sh.nrows): 
            row =  sh.row_values(rownum)
            fileno, subject, body, label = row[0], clean_text(row[1]), clean_text(row[2]), str(row[3])
            
            if label == '4.0' or label == '5.0':
                label = '5.0'
            
            mlp_data.append((label,body))

    print "mlp data loaded"
    return mlp_data

def write_mlp_data(data,fname):
    f = open(fname,"w")
    for label, text in data:
        f.write(label+"\t"+text)
        f.write("\n")
    f.close()
    

def create_libshort(mlp_data):
    random.shuffle(mlp_data)
    pivot = (len(mlp_data)*7)/10
    train_data = mlp_data[:pivot]
    test_data = mlp_data[pivot:]
    
    write_mlp_data(train_data,"../data/training_data")
    write_mlp_data(test_data,"../data/testing_data")
    print "train, test data written"


if __name__ == "__main__":
    mlp_data = get_mlp_data()
    create_libshort(mlp_data)
