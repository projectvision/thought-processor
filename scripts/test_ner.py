from nltk.tag.stanford import NERTagger

model_path = "../ner/english.muc.7class.distsim.crf.ser.gz"
jar_path = "../ner/stanford-ner.jar"
st = NERTagger(model_path,jar_path)
text = 'Rami Eid is studying at Stony Brook University in NY. He lives in United States of America'
tokens = text.split()
st.tag(tokens) 