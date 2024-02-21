import pandas as pd
import argparse
import os
import sys

import sklearn
import sklearn.model_selection

import spacy
from spacy.lang.ro import Romanian
nlp=spacy.load('ro_core_news_sm')

#allowed={
#    "PER":True,
#    "LOC":True,
#    "ORG":True,
#}

labels={}

def processFile(ftxt, fann):
    global labels

    #print(ftxt, fann)
    with open(ftxt,"rb") as f: text=f.read()
    with open(ftxt,"r") as f: text1=f.read()
    doc = nlp(text1)
    start=0
    tokens=[]
    #textb=text #bytes(text,encoding="utf-8")
    textb=text.decode("utf-8")
    for sent in doc.sents:
        for token in sent:
            #print(token.text, token.i, token.idx)

            t=token.text.strip()
            if len(t)==0: continue
            #t=bytes(t,encoding="utf-8")
            pos=textb.find(t,start)
            if pos!=-1:
                tokens.append({"text":t,"idx":pos})
                #print(t,pos)
                start=pos+len(t)
        tokens.append({"text":False})

    #sys.exit(-1)

    ann=[]

    with open(fann,"r") as f:
        for line in f :
            data=line.split("\t")
            if len(data)!=3: continue
            data[1]=data[1].split(" ")
            if len(data[1])!=3: continue
            data[1][1]=int(data[1][1])
            data[1][2]=int(data[1][2])

            #print(data)

            ann.append(data[1])

    ret=[]

    current=[]
    clabel="O"
    for token in tokens:
        if token["text"]==False:
            if len(current)>0:
                ret.append(current)
                current=[]
            continue

        found=False
        for a in ann:
            if a[1]<=token['idx'] and token['idx']+len(token['text'])<=a[2]:
                found=a
                break
        #print(token['text'], found)
        if found==False:
            label="O"
        else:
            label=found[0]
        
        if label!="O":
            if clabel==label: 
                label="I-"+label
            else: 
                clabel=label
                label="B-"+label
        else: clabel=label

        labels[label]=True
        current.append([token['text'],"_","_",label])

    if len(current)>0: ret.append(current)
    return ret

parser=argparse.ArgumentParser()
parser.add_argument("--corpus", help="Corpus", required=True)
args=parser.parse_args()

annFolder="gold_standoff"
filesFolder="files"

if not os.path.exists(args.corpus) or not os.path.exists(os.path.join(args.corpus,filesFolder)) or not os.path.exists(os.path.join(args.corpus,annFolder)):
    print("{} is not a valid corpus".format(args.corpus))
    sys.exit(-1)

numFiles=0
data=[]
for filename in os.listdir(os.path.join(args.corpus,annFolder)):
    if not filename.endswith(".ann"): continue

    fann1 = os.path.join(args.corpus,annFolder, filename)
    
    filename=filename[:-4]+".txt"
    ftxt1 = os.path.join(args.corpus,filesFolder, filename)

    if os.path.isfile(fann1) and os.path.isfile(ftxt1):
        numFiles+=1
        f1=processFile(ftxt1,fann1)

        data+=f1

print("Num files: {}".format(numFiles))
print("Num sentences: {}".format(len(data)))

labels=list(labels.keys())
print("Num Labels: {}".format(len(labels)))
print("Labels:")
print(",".join(labels))

with open("labels.txt","w") as f: f.write(",".join(labels))

train, test1 = sklearn.model_selection.train_test_split(data,test_size=0.4, shuffle=True)
test, dev = sklearn.model_selection.train_test_split(test1,test_size=0.5, shuffle=True)

print("Sentences TRAIN={} VALID={} TEST={}".format(len(train), len(dev), len(test)))

tokens=0
with open("data_xlmr/train.txt","w") as f:
    for sent in train:
        for token in sent:
            tokens+=1
            f.write(" ".join(token))
            f.write("\n")
        f.write("\n")
print("Tokens TRAIN={}".format(tokens))

tokens=0
with open("data_xlmr/test.txt","w") as f:
    for sent in test:
        for token in sent:
            tokens+=1
            f.write(" ".join(token))
            f.write("\n")
        f.write("\n")
print("Tokens TEST={}".format(tokens))

tokens=0
with open("data_xlmr/valid.txt","w") as f:
    for sent in dev:
        for token in sent:
            tokens+=1
            f.write(" ".join(token))
            f.write("\n")
        f.write("\n")
print("Tokens VALID={}".format(tokens))
