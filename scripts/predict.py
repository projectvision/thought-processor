
from label_map import label_dict
from libshorttext.classifier import *
from classify import clean_text
import sys


m = TextModel()
model_path = sys.argv[1]
m.load(model_path)
print "Model loaded. Enter text to classify. press q for quit"

while 1:
    text = raw_input()
    if text == "q":
        sys.exit(1)
    new_text = clean_text(text)
    label_id = predict_single_text(str(new_text),m)
    label_name = label_dict[label_id]
    print "label: ",label_name

